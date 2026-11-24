#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update Lab5 docx for broadened HTTP flood PCRE rule (sid 1000002)."""
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

BASE = Path(__file__).resolve().parents[2]
DOC = BASE / "Ашомка_Андрій_ІМ-34_ЛР5.docx"
SESSION = BASE / "evidence" / "console" / "sessions" / "11-suricata-custom.txt"
COLOR = RGBColor(0x1F, 0x29, 0x37)

THRESHOLDS = (
    "Обґрунтування порогів: значення підібрано відносно базової лінії. Для SYN-сканування — "
    "50 пакетів за 5 с (проти 1–2 SYN/с у легітимних клієнтів) із умовою window:1024, щоб не "
    "плутати зі SYN HTTP-flood (window 64240). Для HTTP flood — 80 запитів за 2 с (проти ~1–2 req/с "
    "фону); URI-шаблон pcre:\"/\\/\\?[A-Za-z0-9]+/\" ловить GET /?<випадковий рядок> з цифр і/або "
    "літер (у цьому дампі — цифри; літери теж покриті, щоб атакувальник не обійшов правило "
    "простою заміною алфавіту). Для ICMP-розвідки — 5 echo за 2 с за майже нульового ICMP у нормі."
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


def replace_runs(p, text, *, bold_prefix="", size=12, name="Times New Roman"):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        set_run_font(r1, bold=True, size=size, name=name)
        rest = text[len(bold_prefix) :] if text.startswith(bold_prefix) else text
        r2 = p.add_run(rest)
        set_run_font(r2, bold=False, size=size, name=name)
    else:
        run = p.add_run(text)
        set_run_font(run, size=size, name=name)


def main():
    session_body = SESSION.read_text(encoding="utf-8").strip()
    doc = Document(str(DOC))

    # Update console table that contains custom local.rules / suricata custom run
    updated_table = False
    for tbl in doc.tables:
        if len(tbl.rows) != 1 or len(tbl.columns) != 1:
            continue
        cell = tbl.rows[0].cells[0]
        text = cell.text
        if "local.rules" in text and ("1000002" in text or "HTTP Flood" in text or "-S /custom/local.rules" in text):
            cell.text = ""
            run = cell.paragraphs[0].add_run(session_body)
            set_run_font(run, size=9, name="Consolas")
            updated_table = True
            break

    # Update thresholds / PCRE description paragraph
    updated_para = False
    for p in doc.paragraphs:
        t = p.text
        if t.startswith("Обґрунтування порогів:") or (
            "HTTP flood 80" in t and "window:1024" in t
        ) or (
            t.startswith("Пороги:") and "HTTP flood" in t
        ):
            replace_runs(p, THRESHOLDS, bold_prefix="Обґрунтування порогів: ")
            updated_para = True
            break

    if not updated_table:
        print("WARN: custom-rules console table not found")
    if not updated_para:
        print("WARN: thresholds paragraph not found")

    try:
        doc.save(str(DOC))
        print(f"SAVED {DOC} table={updated_table} para={updated_para}")
    except PermissionError:
        alt = DOC.with_name(DOC.stem + "_http_rule.docx")
        doc.save(str(alt))
        print(f"LOCKED; saved {alt}")


if __name__ == "__main__":
    main()
