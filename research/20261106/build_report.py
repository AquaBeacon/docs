from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "AquaBeacon_研究レポート.md"
OUTPUT = HERE / "AquaBeacon_研究レポート.docx"
FONT = "Yu Mincho"


def set_run_font(run, name: str = FONT, size: float | None = None, bold: bool | None = None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attr}"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def style_font(style, size: float, bold: bool = False):
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style._element.get_or_add_rPr()
    fonts = rpr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attr}"), FONT)


def set_cell_shading(cell, fill: str):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def set_table_borders_and_padding(table):
    tblpr = table._tbl.tblPr
    borders = tblpr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tblpr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "D9D9D9")
    margins = tblpr.find(qn("w:tblCellMar"))
    if margins is None:
        margins = OxmlElement("w:tblCellMar")
        tblpr.append(margins)
    for edge in ("top", "start", "bottom", "end"):
        element = margins.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            margins.append(element)
        element.set(qn("w:w"), "70")
        element.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    trpr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    trpr.append(repeat)


def prevent_row_split(row):
    trpr = row._tr.get_or_add_trPr()
    trpr.append(OxmlElement("w:cantSplit"))


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_run_font(run, size=9)


def add_inline(paragraph, text: str):
    # Retain readable link text and its URL, while keeping the original Markdown source authoritative.
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1（\2）", text)
    pattern = re.compile(r"(\*\*.*?\*\*|`[^`]+`|\*[^*]+\*)")
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos:match.start()])
            set_run_font(run)
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, bold=True)
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, name="Consolas", size=9.5)
        else:
            run = paragraph.add_run(token[1:-1])
            set_run_font(run)
            run.italic = True
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run)


def table_cells(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", line))


def add_table(doc: Document, lines: list[str]):
    rows = [table_cells(line) for line in lines if not is_table_separator(line)]
    if not rows:
        return
    cols = max(map(len, rows))
    table = doc.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"
    set_table_borders_and_padding(table)
    table.autofit = True
    for ri, values in enumerate(rows):
        row = table.rows[ri]
        prevent_row_split(row)
        for ci in range(cols):
            cell = row.cells[ci]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            if ri < len(rows) - 1 and len(rows) <= 3:
                p.paragraph_format.keep_with_next = True
            elif ri == 0:
                p.paragraph_format.keep_with_next = True
            value = values[ci] if ci < len(values) else ""
            add_inline(p, value)
            for run in p.runs:
                set_run_font(run, size=8.5, bold=(ri == 0))
            if ri == 0:
                set_cell_shading(cell, "EAEAEA")
        if ri == 0:
            set_repeat_table_header(row)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def build(source: Path = SOURCE, output: Path = OUTPUT):
    markdown = source.read_text(encoding="utf-8-sig")
    lines = markdown.splitlines()
    doc = Document()
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(22)
    section.bottom_margin = Mm(20)
    section.left_margin = Mm(23)
    section.right_margin = Mm(23)
    section.footer_distance = Mm(10)

    styles = doc.styles
    normal = styles["Normal"]
    style_font(normal, 10.5)
    normal.paragraph_format.line_spacing = 1.25
    normal.paragraph_format.space_after = Pt(5)
    title = styles["Title"]
    style_font(title, 19, True)
    title.paragraph_format.space_after = Pt(12)
    for name, size in (("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 10.5)):
        style = styles[name]
        style_font(style, size, True)
        style.paragraph_format.space_before = Pt(12 if name != "Heading 3" else 8)
        style.paragraph_format.space_after = Pt(5)
        style.paragraph_format.keep_with_next = True

    # Remove any inherited paragraph borders, including the built-in Title rule.
    for style in styles:
        ppr = style._element.pPr
        if ppr is not None:
            pborder = ppr.find(qn("w:pBdr"))
            if pborder is not None:
                ppr.remove(pborder)

    add_page_number(section.footer.paragraphs[0])
    i = 0
    first_h1 = True
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            add_table(doc, table_lines)
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip().strip("# ")
            if level == 1 and first_h1:
                p = doc.add_paragraph(style="Title")
                first_h1 = False
            else:
                # Markdown H1 is the document title; shift subsequent levels down one.
                p = doc.add_paragraph(style=f"Heading {min(max(level - 1, 1), 3)}")
            add_inline(p, text)
            ppr = p._p.get_or_add_pPr()
            pborder = ppr.find(qn("w:pBdr"))
            if pborder is not None:
                ppr.remove(pborder)
            i += 1
            continue
        bullet = re.match(r"^\s*[-*+]\s+(.*)$", line)
        numbered = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if bullet or numbered:
            p = doc.add_paragraph(style="List Bullet" if bullet else "List Number")
            add_inline(p, (bullet or numbered).group(1))
            for run in p.runs:
                set_run_font(run)
            i += 1
            continue
        # Join wrapped Markdown source lines into a single paragraph; blank lines delimit paragraphs.
        chunks = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("#", "|", "- ", "* ", "+ ")) and not re.match(r"^\s*\d+[.)]\s+", lines[i]):
            chunks.append(lines[i].strip())
            i += 1
        p = doc.add_paragraph()
        add_inline(p, " ".join(chunks))
        if re.match(r"^表\s*\d+", chunks[0]):
            p.paragraph_format.keep_with_next = True

    doc.core_properties.title = "AquaBeacon 研究レポート"
    doc.core_properties.subject = "光学・音響・慣性計測による水中相対位置推定とマッピング"
    doc.core_properties.author = ""
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE,
          Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT)
