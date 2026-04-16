from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Set

from .doc_converter import DocToDocxConverter
from .docx_handler import DocxRedactionHandler
from .patterns import FieldRule, build_field_rules
from .pdf_handler import PdfRedactionHandler


@dataclass(frozen=True)
class RedactionOptions:
    selected_fields: Set[str]
    custom_keywords: List[str]
    redact_custom: bool = False


@dataclass(frozen=True)
class TextMatch:
    start: int
    end: int
    field: str
    original: str
    replacement: str


class TextRedactor:
    def __init__(self, field_rules: Dict[str, FieldRule]) -> None:
        self.field_rules = field_rules

    def redact_text(self, text: str, options: RedactionOptions) -> str:
        matches = self.collect_matches(text, options)
        if not matches:
            return text

        redacted = text
        for match in sorted(matches, key=lambda item: item.start, reverse=True):
            redacted = redacted[: match.start] + match.replacement + redacted[match.end :]
        return redacted

    def collect_matches(self, text: str, options: RedactionOptions) -> List[TextMatch]:
        matches: List[TextMatch] = []

        for field in options.selected_fields:
            rule = self.field_rules.get(field)
            if not rule:
                continue

            for pattern_spec in rule.patterns:
                for found in pattern_spec.pattern.finditer(text):
                    value = found.group(pattern_spec.group)
                    if not value or not value.strip():
                        continue
                    start, end = found.span(pattern_spec.group)
                    matches.append(
                        TextMatch(
                            start=start,
                            end=end,
                            field=field,
                            original=value,
                            replacement=self._replacement_for(field, value),
                        )
                    )

        if options.redact_custom:
            matches.extend(self._custom_keyword_matches(text, options.custom_keywords))

        return self._deduplicate_and_resolve(matches)

    def _custom_keyword_matches(self, text: str, keywords: Sequence[str]) -> List[TextMatch]:
        matches: List[TextMatch] = []
        for keyword in sorted(set(keywords), key=len, reverse=True):
            for found in re.finditer(re.escape(keyword), text, flags=re.IGNORECASE):
                original = found.group(0)
                matches.append(
                    TextMatch(
                        start=found.start(),
                        end=found.end(),
                        field="custom",
                        original=original,
                        replacement="*" * max(3, len(original)),
                    )
                )
        return matches

    def _deduplicate_and_resolve(self, matches: Sequence[TextMatch]) -> List[TextMatch]:
        unique_matches = sorted(
            set(matches),
            key=lambda item: (item.start, -(item.end - item.start)),
        )
        resolved: List[TextMatch] = []

        for match in unique_matches:
            if not resolved:
                resolved.append(match)
                continue

            previous = resolved[-1]
            if match.start >= previous.end:
                resolved.append(match)

        return resolved

    def _replacement_for(self, field: str, original: str) -> str:
        if field == "name":
            return "XXX"
        if field == "id_card":
            return "*" * max(6, len(original))
        if field == "phone":
            return "*" * max(6, len(original))
        if field == "email":
            return "***@***.***"
        if field == "address":
            return "******"
        if field == "company":
            return "******公司" if original.endswith("公司") else "******"
        return "*" * max(3, len(original))


class DocumentRedactionService:
    def __init__(self) -> None:
        self.field_rules = build_field_rules()
        self.text_redactor = TextRedactor(self.field_rules)
        self.doc_converter = DocToDocxConverter()
        self.docx_handler = DocxRedactionHandler(self.text_redactor)
        self.pdf_handler = PdfRedactionHandler(self.text_redactor)

    def available_fields(self) -> List[FieldRule]:
        return list(self.field_rules.values())

    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        options: RedactionOptions,
    ) -> Path:
        suffix = input_path.suffix.lower()
        if suffix == ".doc":
            return self._process_doc_file(input_path, output_path, options)
        if suffix == ".docx":
            return self.docx_handler.process(input_path, output_path, options)
        if suffix == ".pdf":
            return self.pdf_handler.process(input_path, output_path, options)
        raise ValueError("仅支持 .doc、.docx 和 .pdf 文件。")

    def _process_doc_file(
        self,
        input_path: Path,
        output_path: Path,
        options: RedactionOptions,
    ) -> Path:
        with tempfile.TemporaryDirectory(prefix="doc_convert_") as temp_dir:
            converted_path = self.doc_converter.convert(input_path, Path(temp_dir))
            normalized_output = output_path.with_suffix(".docx")
            return self.docx_handler.process(converted_path, normalized_output, options)

    @staticmethod
    def parse_custom_keywords(raw_text: str) -> List[str]:
        if not raw_text:
            return []
        parts = re.split(r"[\n,，;；]+", raw_text)
        seen = []
        for part in parts:
            keyword = part.strip()
            if keyword and keyword not in seen:
                seen.append(keyword)
        return seen
