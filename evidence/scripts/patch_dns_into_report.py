#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert DNS sample command/output/flag explanations into the current Lab5 docx."""
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

BASE = Path(__file__).resolve().parents[2]
DOC = BASE / "Ашомка_Андрій_ІМ-34_ЛР5.docx"
SESS = BASE / "evidence" / "console" / "sessions" / "02b-dns-sample.txt"
COLOR = RGBColor(0x1F, 0x29, 0x37)

INTRO = (
    "Роль DNS і ім’я хоста shop.lab.local підтверджено окремою командою tshark у PowerShell "
    "(файл evidence/console/dns-sample.txt). Змінні $pcap / $out задають шляхи до дампу й каталогу "
    "evidence; $env:TZ=UTC узгоджує час із UTC у звіті."
)
LABEL = "Вивід консолі (PowerShell: DNS за участю 10.42.48.2 → dns-sample.txt):"
FLAGS = (
    "Пояснення прапорців tshark у цій команді: "
    "-r — читати готовий дамп (не live-захоплення); "
    '-Y "dns && ip.addr==10.42.48.2" — display-фільтр: лише DNS-пакети за участю DNS-сервера сегмента '
    "(так підтверджуємо його роль і бачимо імена, які він обслуговує); "
    "-T fields — виводити окремі поля замість повного розбору пакета; "
    "-e frame.time_utc / -e ip.src / -e ip.dst / -e dns.qry.name / -e dns.a — колонки: час UTC, "
    "адреси, запитуване ім’я та A-запис у відповіді (у чистому запиті dns.a порожній); "
    "2>&1 — об’єднати stderr із stdout у PowerShell; "
    "Select-Object -First 15 — коротка вибірка перших 15 рядків для evidence; "
    "Set-Content — записати результат у dns-sample.txt. "
    "У виводі видно пари запит/відповідь: клієнти питають shop.lab.local у 10.42.48.2, "
    "відповідь містить A=10.42.48.18; рядок із time.example.net — інший DNS-запит того ж сервера "
    "у тій самій вибірці «перших 15»."
)


def set_run_font(run, *, bold=False, size=12, name="Times New Roman"):
    run.bold = bold
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = COLOR
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(f"w:{a}"), name)


def insert_paragraph_after(paragraph, text="", *, first_line=True, space_after=6, size=12, name="Times New Roman"):
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    pf = new_para.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.first_line_indent = Cm(1.25 if first_line and text else 0)
    if text:
        run = new_para.add_run(text)
        set_run_font(run, size=size, name=name)
    return new_para


def insert_table_after(doc, paragraph, text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    cell.text = ""
    run = cell.paragraphs[0].add_run(text)
    set_run_font(run, size=9, name="Consolas")
    tbl_el = tbl._tbl
    tbl_el.getparent().remove(tbl_el)
    paragraph._p.addnext(tbl_el)
    spacer = OxmlElement("w:p")
    tbl_el.addnext(spacer)
    return Paragraph(spacer, paragraph._parent)


def main():
    body = SESS.read_text(encoding="utf-8").strip()
    doc = Document(str(DOC))
    joined = "\n".join(p.text for p in doc.paragraphs)
    if "dns-sample.txt" in joined and "dns && ip.addr==10.42.48.2" in joined:
        print("already present")
        return

    anchor = None
    for p in doc.paragraphs:
        if p.text.startswith("Інтерпретація: Сегмент 10.42.48.0/24"):
            anchor = p
            break
    if anchor is None:
        raise SystemExit("anchor paragraph not found")

    cur = insert_paragraph_after(anchor, INTRO, first_line=True, space_after=6)
    cur = insert_paragraph_after(cur, LABEL, first_line=False, space_after=2)
    cur = insert_table_after(doc, cur, body)
    insert_paragraph_after(cur, FLAGS, first_line=True, space_after=8)

    try:
        doc.save(str(DOC))
        print(f"saved {DOC}")
    except PermissionError:
        alt = DOC.with_name(DOC.stem + "_dns.docx")
        doc.save(str(alt))
        print(f"docx locked; saved {alt}")


if __name__ == "__main__":
    main()
