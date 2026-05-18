from pathlib import Path
from unittest.mock import patch

from docx import Document

from app import Config, app, build_upload_name


def test_build_upload_name_preserves_docx_suffix_for_chinese_filename():
    with patch("app.uuid4") as uuid4:
        uuid4.return_value.hex = "abcdef1234567890"

        upload_name = build_upload_name("测试文档.docx")

    assert upload_name == "abcdef12_document.docx"
    assert Path(upload_name).suffix == ".docx"


def test_build_upload_name_preserves_pdf_suffix_for_chinese_filename():
    with patch("app.uuid4") as uuid4:
        uuid4.return_value.hex = "abcdef1234567890"

        upload_name = build_upload_name("敏感信息.pdf")

    assert upload_name == "abcdef12_document.pdf"
    assert Path(upload_name).suffix == ".pdf"


def test_post_accepts_docx_with_chinese_filename(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    processed_dir = tmp_path / "processed"
    upload_dir.mkdir()
    processed_dir.mkdir()
    monkeypatch.setattr(Config, "UPLOAD_FOLDER", upload_dir)
    monkeypatch.setattr(Config, "PROCESSED_FOLDER", processed_dir)
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(upload_dir))
    monkeypatch.setitem(app.config, "PROCESSED_FOLDER", str(processed_dir))
    monkeypatch.setitem(app.config, "TESTING", True)

    input_docx = tmp_path / "input.docx"
    document = Document()
    document.add_paragraph("手机号：13812345678")
    document.save(input_docx)

    with input_docx.open("rb") as file_obj:
        response = app.test_client().post(
            "/",
            data={
                "file": (file_obj, "测试文档.docx"),
                "field_phone": "on",
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert "文件脱敏完成".encode() in response.data
    outputs = list(processed_dir.glob("*.docx"))
    assert len(outputs) == 1
