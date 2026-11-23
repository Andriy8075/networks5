#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand §5.3.2 role justifications in the current Lab5 docx."""
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

BASE = Path(__file__).resolve().parents[2]
DOC = BASE / "Ашомка_Андрій_ІМ-34_ЛР5.docx"
COLOR = RGBColor(0x1F, 0x29, 0x37)

MARKER = "як саме з дампу lr5_v02.pcap виведено роль кожного вузла"

PARAS = [
    (
        "Інтерпретація: Сегмент 10.42.48.0/24 (усі внутрішні адреси в Endpoints мають префікс 10.42.48.). "
        "Нижче — як саме з дампу lr5_v02.pcap виведено роль кожного вузла (не лише «яка IP», "
        "а за якими командами/фільтрами)."
    ),
    (
        "Вебсервер 10.42.48.18:80 (shop.lab.local). У виводі tshark -q -z endpoints,ip адреса .18 "
        "має найбільший обсяг (≈63587 пакетів / ≈5693 kB) — майже весь трафік сегмента пов’язаний з нею. "
        "У Conversations (conv,ip) більшість топ-розмов — це «хтось ↔ 10.42.48.18». "
        "Фільтр http.request показує TCP/80 і заголовок Host: shop.lab.local на цій IP. "
        "Додатково DNS віддає A-запис shop.lab.local → 10.42.48.18 (див. dns-sample.txt нижче). "
        "Висновок: .18 — вебсервіс, на який скаржилися щодо недоступності."
    ),
    (
        "DNS 10.42.48.2. У Endpoints вузол .2 має помірний трафік; у Protocol Hierarchy є DNS. "
        'Команда tshark -Y "dns && ip.addr==10.42.48.2" -T fields … показує: клієнти шлють запити '
        "саме на .2, а відповіді містять dns.a=10.42.48.18 для shop.lab.local. "
        "У conv,ip є розмова 10.42.48.2 ↔ 9.9.9.9 — зовнішні імена .2 форвардить на рекурсивний "
        "резолвер 9.9.9.9. Тому .2 — DNS-сервер сегмента, а не веб і не шлюз."
    ),
    (
        "Шлюз 10.42.48.1 (MAC 02:9e:28:0f:b4:09). У Endpoints у .1 майже немає IP-пакетів як у "
        "кінцевої служби (лише одиниці) — це нормально для default gateway: трафік назовні "
        "адресований зовнішнім IP, а не на .1. Роль видно на L2/ARP: "
        'tshark -Y "arp && arp.proto_ipv4==10.42.48.1" дає MAC 02:9e:28:0f:b4:09; '
        "у кадрах до/від зовнішніх адрес (9.9.9.9, джерела HTTP flood) цей MAC — сторона шлюза. "
        "Шлюз тут — маршрутизатор сегмента, не reverse-proxy/nginx перед .18: клієнти ходять "
        "на вебсервер напряму в тій самій підмережі."
    ),
    (
        "Легітимні клієнти .38 .42 .43 .51 .56 .59 .88. У Endpoints це сім внутрішніх адрес "
        "із стабільним помірним обсягом. Фільтр "
        "http.request && ip.src==10.42.48.0/24 && ip.dst==10.42.48.18 показує з них GET на "
        "/, /health, /api/*, /static/* з Host shop.lab.local протягом майже всього дампу "
        "(розмови з .18 мають велику Duration у conv,ip). Вони не є джерелом ARP-обходу й "
        "не шлють сплеск SYN на сотні портів. Тому їх віднесено до нормальних клієнтів магазину "
        "(базова лінія в наступному пункті)."
    ),
    (
        "Внутрішній атакувальник (розвідка + скан) 10.42.48.126. Адреса в тій самій підмережі, "
        "що й сервер (внутрішня мережа — як зазначено в завданні для HOME_NET/EXTERNAL_NET). "
        "Після Endpoints видно сплеск активності .126. Фільтри "
        "arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126 та icmp.type==8 && ip.src==10.42.48.126 "
        "фіксують ARP-обхід і ICMP echo з .126; "
        "ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0 — SYN-скан портів .18 "
        "(≈1029 портів, window 1024). Підрахунок SYN без ACK за джерелом також піднімає .126 "
        "серед лідерів. Це не «звичайний клієнт сайту», а джерело розвідки й сканування всередині LAN."
    ),
    (
        "Зовнішні джерела HTTP flood (8 адрес поза 10.42.48.0/24). У Endpoints/Conversations "
        "топ за обсягом після .18 займають адреси на кшталт 54.85.25.140, 168.2.105.253 тощо. "
        "Фільтр http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24) дає ≈6160 GET "
        "/?<випадкове> у вікні ~09:06:22–09:06:59 UTC з восьми унікальних зовнішніх IP. "
        "Вони не в сегменті сервера; на L2 трафік заходить через шлюз. Це окремий етап DoS, "
        "не той самий вузол, що .126."
    ),
]


def set_run_font(run, *, size=12, name="Times New Roman"):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = COLOR
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(f"w:{a}"), name)


def insert_paragraph_after(paragraph, text, *, first_line=True, space_after=6):
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    pf = new_para.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.first_line_indent = Cm(1.25 if first_line and text else 0)
    if text:
        run = new_para.add_run(text)
        set_run_font(run)
    return new_para


def main():
    doc = Document(str(DOC))
    joined = "\n".join(p.text for p in doc.paragraphs)
    if MARKER in joined:
        print("already present")
        return

    anchor = None
    for p in doc.paragraphs:
        if p.text.startswith("Інтерпретація: Сегмент 10.42.48.0/24"):
            anchor = p
            break
    if anchor is None:
        raise SystemExit("anchor not found")

    # Replace short interpretation with first expanded paragraph
    for r in list(anchor.runs):
        r._element.getparent().remove(r._element)
    run = anchor.add_run(PARAS[0])
    set_run_font(run)
    anchor.paragraph_format.first_line_indent = Cm(1.25)
    anchor.paragraph_format.space_after = Pt(6)

    cur = anchor
    for text in PARAS[1:]:
        cur = insert_paragraph_after(cur, text, first_line=True, space_after=6)

    # Soften the following DNS intro if it still says "підтверджено окремою"
    for p in doc.paragraphs:
        if p.text.startswith("Роль DNS і ім’я хоста shop.lab.local підтверджено окремою"):
            for r in list(p.runs):
                r._element.getparent().remove(r._element)
            run = p.add_run(
                "Роль DNS і ім’я хоста shop.lab.local додатково зафіксовано командою tshark у PowerShell "
                "(файл evidence/console/dns-sample.txt). Змінні $pcap / $out задають шляхи до дампу й каталогу "
                "evidence; $env:TZ=UTC узгоджує час із UTC у звіті."
            )
            set_run_font(run)
            break

    try:
        doc.save(str(DOC))
        print(f"saved {DOC}")
    except PermissionError:
        alt = DOC.with_name(DOC.stem + "_roles.docx")
        doc.save(str(alt))
        print(f"locked; saved {alt}")


if __name__ == "__main__":
    main()
