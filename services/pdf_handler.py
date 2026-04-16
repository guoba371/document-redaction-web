from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import fitz


class PdfRedactionHandler:
    def __init__(self, text_redactor) -> None:
        self.text_redactor = text_redactor

    def process(self, input_path: Path, output_path: Path, options) -> Path:
        document = fitz.open(str(input_path))

        for page in document:
            page_text = page.get_text("text")
            matches = self.text_redactor.collect_matches(page_text, options)
            if not matches:
                continue

            terms = self._group_terms(matches)
            added_annotations = False

            for phrase, payload in terms.items():
                rects = page.search_for(phrase)
                if not rects:
                    continue

                for rect in rects[: payload["count"]]:
                    page.add_redact_annot(
                        rect,
                        text=payload["replacement"],
                        fill=(1, 1, 1),
                        text_color=(0, 0, 0),
                        fontsize=max(8, min(12, rect.height * 0.7)),
                        align=fitz.TEXT_ALIGN_LEFT,
                    )
                    added_annotations = True

            if added_annotations:
                page.apply_redactions()

        document.save(str(output_path), garbage=4, deflate=True)
        document.close()
        return output_path

    def _group_terms(self, matches):
        grouped = OrderedDict()
        ordered_matches = sorted(
            matches,
            key=lambda item: (-(len(item.original)), item.start),
        )

        for match in ordered_matches:
            phrase = match.original.strip()
            if not phrase:
                continue
            if phrase not in grouped:
                grouped[phrase] = {"replacement": match.replacement, "count": 0}
            grouped[phrase]["count"] += 1

        return grouped
