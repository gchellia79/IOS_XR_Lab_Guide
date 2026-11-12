#!/usr/bin/env python3
"""Extract a Word document into credential-masked Markdown and ordered images."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph


CREDENTIAL_RE = re.compile(
    r"(?i)\b(password|passwd|secret|token)\b"
    r"(\s*(?:[:=]\s*|\s+)(?:(?:is|with)\s+)?(?:[0-9]+\s+)?)"
    r"(\"[^\"\n]*\"|'[^'\n]*'|<[^>\n]*>|[^\s,;]+)"
)
FONT_NAMES = {"consolas", "courier", "courier new", "menlo", "monaco"}


class Extractor:
    def __init__(self, document, output: Path) -> None:
        self.document = document
        self.output = output
        self.images = output / "images"
        self.images.mkdir(parents=True, exist_ok=True)
        self.image_count = 0
        self.table_count = 0
        self.masked_count = 0
        self.headings: list[tuple[int, str]] = []
        self.warnings: list[str] = []

    def mask(self, text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            self.masked_count += 1
            return f"{match.group(1)}{match.group(2)}<masked>"

        text = CREDENTIAL_RE.sub(replace, text)
        if re.search(r"login|log\s*in|username|password", text, re.I):
            def replace_pair(match: re.Match[str]) -> str:
                if match.group().lower() == "username/password":
                    return match.group()
                self.masked_count += 1
                return "<username>/<masked>"

            text = re.sub(r"\b[A-Za-z0-9_.!@+-]+/[A-Za-z0-9_.!@+-]+\b", replace_pair, text)
        return text

    def image(self, element) -> str:
        relationship = element.get(qn("r:embed")) or element.get(qn("r:id"))
        if not relationship:
            self.warnings.append("An image has no embedded relationship; inspect the original.")
            return "<!-- TODO: external or unsupported image -->"
        part = self.document.part.related_parts.get(relationship)
        if part is None:
            self.warnings.append("An embedded image relationship could not be resolved.")
            return "<!-- TODO: missing embedded image -->"
        self.image_count += 1
        extension = Path(str(part.partname)).suffix.lower()
        filename = f"image{self.image_count:02d}{extension}"
        (self.images / filename).write_bytes(part.blob)
        if extension in {".emf", ".wmf", ".tif", ".tiff"}:
            self.warnings.append(f"{filename} needs a browser-compatible image conversion.")
        return f"![image{self.image_count:02d}](images/{filename})"

    def inline_events(self, element):
        for child in element:
            if child.tag == qn("w:txbxContent"):
                yield "textbox", child
            elif child.tag in {qn("a:blip"), "{urn:schemas-microsoft-com:vml}imagedata"}:
                yield "image", child
            elif child.tag == qn("w:t"):
                yield "text", child.text or ""
            elif child.tag == qn("w:tab"):
                yield "text", "\t"
            elif child.tag in {qn("w:br"), qn("w:cr")}:
                yield "text", "\n"
            elif child.tag == "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent":
                candidates = list(child)
                if candidates:
                    yield from self.inline_events(candidates[0])
            else:
                yield from self.inline_events(child)

    def heading_level(self, paragraph: Paragraph, text: str) -> int | None:
        style = paragraph.style
        name = style.name if style is not None else ""
        match = re.match(r"(?:Heading|Titre)\s*(\d+)$", name, re.I)
        if match:
            return min(int(match.group(1)), 6)
        properties = paragraph._p.pPr
        if properties is not None and properties.outlineLvl is not None:
            return min(int(properties.outlineLvl.val) + 1, 6)
        if re.match(r"^Exercise\s+\d", text, re.I) and len(text) < 120:
            return 3
        if re.match(r"^Step\s*:?\s*\d", text, re.I) and len(text) < 50:
            return 4
        if re.match(r"^\d+\.\d+(?:\s+|(?=[A-Za-z]))", text) and len(text) < 100:
            return 2
        return None

    def list_marker(self, paragraph: Paragraph) -> str:
        properties = paragraph._p.pPr
        style = paragraph.style
        style_name = (style.name if style is not None else "").lower()
        if properties is None or properties.numPr is None:
            if style_name.startswith("list bullet"):
                return "- "
            if style_name.startswith("list number"):
                return "1. "
            return ""
        numbering_properties = properties.numPr
        level = int(numbering_properties.ilvl.val) if numbering_properties.ilvl is not None else 0
        number_id = numbering_properties.numId.val if numbering_properties.numId is not None else None
        numbering = self.document.part.numbering_part.element
        definitions = numbering.xpath(f'./w:num[@w:numId="{number_id}"]/w:abstractNumId')
        marker = "- "
        if definitions:
            abstract_id = definitions[0].get(qn("w:val"))
            formats = numbering.xpath(
                f'./w:abstractNum[@w:abstractNumId="{abstract_id}"]'
                f'/w:lvl[@w:ilvl="{level}"]/w:numFmt'
            )
            if formats and formats[0].get(qn("w:val")) != "bullet":
                marker = "1. "
        return "    " * level + marker

    def monospaced(self, paragraph: Paragraph) -> bool:
        style = paragraph.style
        if style is not None:
            if any(word in style.name.lower() for word in ("code", "preformatted", "console")):
                return True
        runs = [run for run in paragraph.runs if run.text.strip()]
        if not runs:
            return False
        inherited = style.font.name if style is not None else None
        fonts = [(run.font.name or inherited or "").lower() for run in runs]
        return all(font in FONT_NAMES or "mono" in font for font in fonts)

    def code(self, text: str) -> str:
        longest = max((len(match.group()) for match in re.finditer(r"`+", text)), default=0)
        fence = "`" * max(3, longest + 1)
        return f"{fence}text\n{text}\n{fence}"

    def paragraph(self, element, force_code: bool = False) -> list[str]:
        paragraph = Paragraph(element, self.document)
        blocks: list[str] = []
        pending: list[str] = []

        def flush() -> None:
            if not pending:
                return
            text = self.mask("".join(pending)).rstrip()
            pending.clear()
            if not text.strip():
                return
            level = self.heading_level(paragraph, text.strip())
            if force_code or self.monospaced(paragraph):
                blocks.append(self.code(text))
            elif level:
                self.headings.append((level, text.strip()))
                blocks.append(f"{'#' * level} {text.strip()}")
            else:
                blocks.append(self.list_marker(paragraph) + text)

        for kind, value in self.inline_events(element):
            if kind == "text":
                pending.append(value)
            else:
                flush()
                if kind == "image":
                    blocks.append(self.image(value))
                else:
                    blocks.extend(self.body(value, force_code=True))
        flush()
        return blocks

    def table(self, element) -> str:
        self.table_count += 1
        rows: list[list[str]] = []
        for row in element.findall(qn("w:tr")):
            cells: list[str] = []
            for cell in row.findall(qn("w:tc")):
                content = "<br>".join(self.body(cell))
                cells.append(content.replace("|", "\\|").replace("\n", "<br>"))
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        rows = [row + [""] * (width - len(row)) for row in rows]
        lines = ["| " + " | ".join(row) + " |" for row in rows]
        lines.insert(1, "| " + " | ".join(["---"] * width) + " |")
        return "\n".join(lines)

    def body(self, element, force_code: bool = False) -> list[str]:
        blocks: list[str] = []
        for child in element:
            if child.tag == qn("w:p"):
                blocks.extend(self.paragraph(child, force_code))
            elif child.tag == qn("w:tbl"):
                blocks.append(self.table(child))
            elif child.tag not in {qn("w:sectPr"), qn("w:tcPr")}:
                blocks.extend(self.body(child, force_code))
        return blocks

    def run(self) -> None:
        blocks = self.body(self.document.element.body)
        (self.output / "draft.md").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
        print("Heading outline:")
        for level, title in self.headings:
            print(f"{'  ' * (level - 1)}{'#' * level} {title}")
        print(f"Images: {self.image_count}")
        print(f"Tables: {self.table_count}")
        print(f"Credential values masked: {self.masked_count}")
        for warning in self.warnings:
            print(f"WARNING: {warning}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--output", "-o", type=Path, default=Path("_import"))
    arguments = parser.parse_args()
    extractor = Extractor(Document(str(arguments.document)), arguments.output)
    extractor.run()


if __name__ == "__main__":
    main()