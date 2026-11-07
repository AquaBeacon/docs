from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
from PIL import Image


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "AquaBeacon_二次審査報告書.md"
OUTPUT = HERE / "AquaBeacon_二次審査報告書.docx"
FONT = "Yu Mincho"
PRINTABLE_WIDTH_MM = 174
MAX_IMAGE_HEIGHT_MM = 45


def set_font(run, size=10, bold=None, italic=None, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attr}"), name)


def set_style(style, size, bold=False):
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


def add_hyperlink(paragraph, label: str, target: str):
    rel_id = paragraph.part.relate_to(
        target,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "000000")
    rpr.append(color)
    fonts = OxmlElement("w:rFonts")
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attr}"), FONT)
    rpr.append(fonts)
    size = OxmlElement("w:sz"); size.set(qn("w:val"), "20")
    rpr.append(size)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rpr.append(underline)
    run.append(rpr)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_inline(paragraph, text: str):
    # Markdown links stay clickable without printing long external URLs.
    token_re = re.compile(r"(\[[^\]]+\]\([^)]+\)|\*\*.*?\*\*|`[^`]+`|\*[^*]+\*)")
    pos = 0
    for match in token_re.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos:match.start()])
            set_font(run)
        token = match.group(0)
        link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", token)
        if link:
            target = link.group(2).strip()
            if target.startswith(("https://", "http://", "mailto:")):
                add_hyperlink(paragraph, link.group(1), target)
            else:
                run = paragraph.add_run(link.group(1))
                set_font(run)
        elif token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_font(run, bold=True)
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_font(run, name="Consolas", size=10)
        else:
            run = paragraph.add_run(token[1:-1])
            set_font(run, italic=True)
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_font(run)


def set_table_style(table, row_count: int, col_count: int):
    table.autofit = False
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "D9D9D9")
        borders.append(el)
    tblpr.append(borders)
    margins = OxmlElement("w:tblCellMar")
    for edge, amount in (("top", 45), ("start", 55), ("bottom", 45), ("end", 55)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), str(amount))
        el.set(qn("w:type"), "dxa")
        margins.append(el)
    tblpr.append(margins)

    # Bias wider columns toward labels/descriptions and narrow columns toward compact metrics.
    ratios_by_count = {
        2: [0.38, 0.62],
        3: [0.30, 0.35, 0.35],
        4: [0.28, 0.24, 0.24, 0.24],
        5: [0.24, 0.19, 0.19, 0.19, 0.19],
        6: [0.21, 0.158, 0.158, 0.158, 0.158, 0.158],
    }
    ratios = ratios_by_count.get(col_count, [1 / col_count] * col_count)
    for ci, ratio in enumerate(ratios):
        width = Mm(PRINTABLE_WIDTH_MM * ratio)
        table.columns[ci].width = width
        for row in table.rows:
            row.cells[ci].width = width
    for ri, row in enumerate(table.rows):
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        if ri == 0:
            header = OxmlElement("w:tblHeader")
            header.set(qn("w:val"), "true")
            trpr.append(header)
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            if ri == 0:
                p.paragraph_format.keep_with_next = True
            for run in p.runs:
                set_font(run, size=10, bold=(ri == 0))
            if ri == 0:
                shade = OxmlElement("w:shd")
                shade.set(qn("w:fill"), "F0F0F0")
                cell._tc.get_or_add_tcPr().append(shade)
    if row_count <= 3:
        for row in table.rows[:-1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True


def parse_table_row(line: str):
    return [x.strip() for x in line.strip().strip("|").split("|")]


def is_separator(line: str):
    return bool(re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", line))


def add_table(doc, lines, page_break=False):
    rows = [parse_table_row(line) for line in lines if not is_separator(line)]
    if not rows:
        return
    cols = max(len(row) for row in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    for ri, values in enumerate(rows):
        for ci in range(cols):
            cell = table.cell(ri, ci)
            cell.text = ""
            add_inline(cell.paragraphs[0], values[ci] if ci < len(values) else "")
            if page_break and ri == 0 and ci == 0:
                cell.paragraphs[0].paragraph_format.page_break_before = True
    set_table_style(table, len(rows), cols)


def fitted_image_size(image_path: Path, max_width_mm: float, max_height_mm: float):
    if not image_path.is_file():
        raise FileNotFoundError(f"Referenced figure not found: {image_path}")
    with Image.open(image_path) as im:
        width_px, height_px = im.size
    scale = min(max_width_mm / width_px, max_height_mm / height_px)
    return Mm(width_px * scale), Mm(height_px * scale)


def add_images(doc, images: list[tuple[str, str]], page_break=False):
    paths = [(caption, (HERE / path).resolve()) for caption, path in images]
    if len(paths) == 1:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        if page_break:
            p.paragraph_format.page_break_before = True
        width, height = fitted_image_size(paths[0][1], 170, 48)
        p.add_run().add_picture(str(paths[0][1]), width=width, height=height)
        return
    table = doc.add_table(rows=1, cols=len(paths))
    table.autofit = False
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}"); el.set(qn("w:val"), "nil"); borders.append(el)
    table._tbl.tblPr.append(borders)
    margins = OxmlElement("w:tblCellMar")
    for edge in ("top", "start", "bottom", "end"):
        el = OxmlElement(f"w:{edge}"); el.set(qn("w:w"), "0"); el.set(qn("w:type"), "dxa"); margins.append(el)
    table._tbl.tblPr.append(margins)
    for ci, (_, image_path) in enumerate(paths):
        cell = table.cell(0, ci)
        cell.width = Mm(82)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        if page_break and ci == 0:
            p.paragraph_format.page_break_before = True
        width, height = fitted_image_size(image_path, 80, 45)
        p.add_run().add_picture(str(image_path), width=width, height=height)


def add_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run()
    set_font(run, size=10)
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t"); text.text = "1"
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, sep, text, end])


def build(source=SOURCE, output=OUTPUT):
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    doc = Document()
    section = doc.sections[0]
    section.page_width = Mm(210); section.page_height = Mm(297)
    section.top_margin = Mm(17); section.bottom_margin = Mm(17)
    section.left_margin = Mm(18); section.right_margin = Mm(18)
    section.footer_distance = Mm(8)
    styles = doc.styles
    normal = styles["Normal"]
    set_style(normal, 10)
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(3.5)
    title = styles["Title"]
    set_style(title, 16, True)
    title.paragraph_format.space_after = Pt(7)
    for name, size in (("Heading 1", 12), ("Heading 2", 11), ("Heading 3", 10)):
        style = styles[name]
        set_style(style, size, True)
        style.paragraph_format.space_before = Pt(6)
        style.paragraph_format.space_after = Pt(2)
        style.paragraph_format.keep_with_next = True
    for style in styles:
        ppr = style._element.pPr
        if ppr is not None:
            border = ppr.find(qn("w:pBdr"))
            if border is not None:
                ppr.remove(border)
    add_footer(section)

    pending_break = False
    first_heading = True
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        if raw.strip() == "<!-- pagebreak -->":
            pending_break = True
            i += 1
            continue
        if not raw.strip():
            i += 1
            continue
        if raw.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip()); i += 1
            add_table(doc, table_lines, pending_break)
            pending_break = False
            continue
        image_matches = list(re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", raw))
        if image_matches and not re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", "", raw).strip():
            add_images(doc, [(m.group(1), m.group(2)) for m in image_matches], pending_break)
            pending_break = False
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", raw)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip().strip("# ")
            if level == 1 and first_heading:
                p = doc.add_paragraph(style="Title")
                first_heading = False
            else:
                p = doc.add_paragraph(style=f"Heading {min(max(level - 1, 1), 3)}")
            add_inline(p, text)
            if pending_break:
                p.paragraph_format.page_break_before = True
                pending_break = False
            i += 1
            continue
        bullet = re.match(r"^\s*[-*+]\s+(.*)$", raw)
        numbered = re.match(r"^\s*\d+[.)]\s+(.*)$", raw)
        if bullet or numbered:
            p = doc.add_paragraph(style="List Bullet" if bullet else "List Number")
            add_inline(p, (bullet or numbered).group(1))
            if pending_break:
                p.paragraph_format.page_break_before = True
                pending_break = False
            i += 1
            continue
        chunks = [raw.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and lines[i].strip() != "<!-- pagebreak -->" and not lines[i].lstrip().startswith(("#", "|", "- ", "* ", "+ ", "![")) and not re.match(r"^\s*\d+[.)]\s+", lines[i]):
            chunks.append(lines[i].strip()); i += 1
        p = doc.add_paragraph()
        add_inline(p, " ".join(chunks))
        if pending_break:
            p.paragraph_format.page_break_before = True
            pending_break = False

    doc.core_properties.title = "AquaBeacon 二次審査報告書"
    doc.core_properties.subject = "水中位置推定システムの開発と実験評価"
    doc.core_properties.author = ""
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE,
          Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT)
