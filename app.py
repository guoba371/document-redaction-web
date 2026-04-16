from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
from services import DocumentRedactionService, RedactionOptions


Config.ensure_directories()

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = str(Config.UPLOAD_FOLDER)
app.config["PROCESSED_FOLDER"] = str(Config.PROCESSED_FOLDER)

redaction_service = DocumentRedactionService()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def build_output_name(original_filename: str) -> str:
    source = Path(original_filename)
    stem = secure_filename(source.stem) or "document"
    suffix = ".docx" if source.suffix.lower() == ".doc" else source.suffix.lower()
    return f"{stem}_redacted_{uuid4().hex[:8]}{suffix}"


@app.route("/", methods=["GET", "POST"])
def index():
    fields = redaction_service.available_fields()
    selected_fields = {field.key for field in fields}
    custom_keywords_text = ""
    enable_custom = False
    result_filename = None

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        selected_fields = {
            field.key
            for field in fields
            if request.form.get(f"field_{field.key}") == "on"
        }
        custom_keywords_text = request.form.get("custom_keywords", "")
        enable_custom = request.form.get("enable_custom") == "on"

        if not uploaded_file or not uploaded_file.filename:
            flash("请先选择一个 .doc、.docx 或 .pdf 文件。", "danger")
        elif not allowed_file(uploaded_file.filename):
            flash("文件格式不支持，仅支持 .doc、.docx 和 .pdf。", "danger")
        else:
            safe_name = secure_filename(uploaded_file.filename)
            upload_name = f"{uuid4().hex[:8]}_{safe_name}"
            upload_path = Config.UPLOAD_FOLDER / upload_name
            output_name = build_output_name(uploaded_file.filename)
            output_path = Config.PROCESSED_FOLDER / output_name

            options = RedactionOptions(
                selected_fields=selected_fields,
                custom_keywords=redaction_service.parse_custom_keywords(custom_keywords_text),
                redact_custom=enable_custom,
            )

            try:
                uploaded_file.save(str(upload_path))
                redaction_service.process_file(upload_path, output_path, options)
                result_filename = output_name
                flash("文件脱敏完成，可以直接下载。", "success")
            except Exception as exc:
                if output_path.exists():
                    output_path.unlink()
                flash(f"处理失败：{exc}", "danger")
            finally:
                if upload_path.exists():
                    upload_path.unlink()

    return render_template(
        "index.html",
        fields=fields,
        selected_fields=selected_fields,
        custom_keywords_text=custom_keywords_text,
        enable_custom=enable_custom,
        result_filename=result_filename,
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}, 200


@app.route("/download/<path:filename>")
def download_file(filename: str):
    return send_from_directory(
        app.config["PROCESSED_FOLDER"],
        filename,
        as_attachment=True,
        download_name=filename,
    )


@app.errorhandler(413)
def file_too_large(_error):
    flash("上传文件过大，请控制在 20MB 以内。", "danger")
    return render_template(
        "index.html",
        fields=redaction_service.available_fields(),
        selected_fields={field.key for field in redaction_service.available_fields()},
        custom_keywords_text="",
        enable_custom=False,
        result_filename=None,
    ), 413


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    app.run(host=host, port=port, debug=debug)
