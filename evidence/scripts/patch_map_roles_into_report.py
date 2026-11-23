#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polish §5.3.2 role justifications in the current Lab5 docx."""
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parents[2]
DOC = BASE / "Ашомка_Андрій_ІМ-34_ЛР5.docx"
COLOR = RGBColor(0x1F, 0x29, 0x37)

# Pairs of (bold_prefix, regular_rest)
REWRITES = [
    (
        "Інтерпретація: ",
        "Усі внутрішні адреси в таблиці Endpoints належать до підмережі 10.42.48.0/24. "
        "Нижче наведено обґрунтування ролі кожного вузла на основі статистики та фільтрів із дампу lr5_v02.pcap.",
    ),
    (
        "Вебсервер 10.42.48.18:80 (shop.lab.local). ",
        "У виводі tshark -q -z endpoints,ip ця адреса має найбільший обсяг трафіку "
        "(63587 пакетів, 5693 kB), а в Conversations (conv,ip) більшість найоб’ємніших розмов "
        "відбувається саме за її участю. За фільтром http.request видно звернення на TCP-порт 80 "
        "із заголовком Host: shop.lab.local, що додатково підтверджується A-записом DNS "
        "(shop.lab.local → 10.42.48.18). Отже, 10.42.48.18 — основний вебсервіс, на недоступність "
        "якого надійшла скарга.",
    ),
    (
        "DNS-сервер 10.42.48.2. ",
        "У Protocol Hierarchy зафіксовано DNS-трафік, а в Endpoints вузол .2 має помірну кількість пакетів. "
        'Команда tshark -Y "dns && ip.addr==10.42.48.2" -T fields … показує, що внутрішні клієнти '
        "надсилають DNS-запити саме на .2, а у відповідь отримують запис A = 10.42.48.18 для shop.lab.local. "
        "Крім того, у conv,ip видно обмін 10.42.48.2 ↔ 9.9.9.9: зовнішні доменні імена локальний "
        "DNS-сервер пересилає на публічний рекурсивний резолвер 9.9.9.9 (Quad9).",
    ),
    (
        "Шлюз 10.42.48.1 (MAC 02:9e:28:0f:b4:09). ",
        "У статистиці IPv4 Endpoints на адресу .1 припадає лише два пакети (ICMP під час розвідки), "
        "оскільки до шлюза майже не звертаються як до кінцевої служби — транзитний трафік адресований "
        "зовнішнім IP. Його роль підтверджується на канальному рівні: фільтр "
        "arp && arp.src.proto_ipv4 == 10.42.48.1 у Wireshark повертає ARP-відповіді з MAC-адресою "
        "02:9e:28:0f:b4:09, і саме цей MAC фігурує в кадрах до/від зовнішніх вузлів "
        "(9.9.9.9, джерела HTTP flood). У цій мережі .1 виконує роль маршрутизатора сегмента "
        "(default gateway), а не проксі перед вебсервером: локальні клієнти звертаються до .18 напряму.",
    ),
    (
        "Легітимні клієнти (.38, .42, .43, .51, .56, .59, .88). ",
        "Це сім внутрішніх адрес із рівномірним помірним обсягом трафіку в Endpoints та тривалими "
        "сесіями з .18 у conv,ip. За фільтром http.request && ip.src==10.42.48.0/24 && ip.dst==10.42.48.18 "
        "видно звичайні GET-запити на /, /health, /api/* і /static/* із заголовком Host: shop.lab.local "
        "протягом майже всього часу захоплення. Жоден із цих вузлів не здійснює ARP-обхід і не надсилає "
        "масових SYN на різні порти, тому їх віднесено до штатних клієнтів сервісу.",
    ),
    (
        "Внутрішній атакувальник 10.42.48.126 (розвідка та сканування). ",
        "Вузол розташований у тій самій підмережі, що й сервер (відповідно до умови завдання щодо "
        "внутрішнього джерела в HOME_NET). У Endpoints помітний підвищений обсяг його трафіку, а фільтри "
        "arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126 та icmp.type==8 && ip.src==10.42.48.126 "
        "виявляють масовий ARP-обхід і ICMP-опитування живих хостів. Далі фільтр "
        "ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0 фіксує SYN-сканування 1029 портів "
        "вебсервера .18 (розмір вікна 1024), що також виводить .126 у лідери за підрахунком SYN без ACK.",
    ),
    (
        "Зовнішні джерела HTTP flood (8 адрес поза 10.42.48.0/24). ",
        "У таблицях Endpoints і Conversations одразу після .18 за обсягом ідуть зовнішні адреси "
        "(зокрема 54.85.25.140, 168.2.105.253 тощо). Фільтр "
        "http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24) виділяє 6160 запитів "
        "GET /?<випадкове> у проміжку 09:06:22–09:06:59 UTC із восьми унікальних зовнішніх IP. "
        "Трафік надходить у сегмент через шлюз і становить окремий етап DoS-атаки, незалежний від "
        "внутрішнього сканера .126.",
    ),
    (
        "",
        "Нижче наведено команду tshark у PowerShell, якою було додатково зафіксовано роль DNS-сервера "
        "10.42.48.2 та прив’язку імені shop.lab.local до 10.42.48.18 (збережено у файлі "
        "evidence/console/dns-sample.txt). Змінні $pcap і $out задають шляхи до дампу та каталогу "
        'evidence, а $env:TZ = "UTC" забезпечує узгодження часових позначок із UTC у звіті.',
    ),
]


def set_run_font(run, *, bold=False, size=12, name="Times New Roman"):
    run.bold = bold
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = COLOR
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(f"w:{a}"), name)


def replace_para(p, bold_prefix: str, rest: str):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        set_run_font(r1, bold=True)
    if rest:
        r2 = p.add_run(rest)
        set_run_font(r2, bold=False)


def main():
    doc = Document(str(DOC))
    start_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.startswith("Інтерпретація: Сегмент 10.42.48.0/24") or p.text.startswith(
            "Інтерпретація: Усі внутрішні адреси"
        ):
            start_idx = i
            break
    if start_idx is None:
        raise SystemExit("start paragraph not found")

    # Verify the 8 paragraphs match the expected range before "Вивід консолі (PowerShell: DNS"
    end_para = doc.paragraphs[start_idx + len(REWRITES)]
    if not end_para.text.startswith("Вивід консолі (PowerShell: DNS"):
        raise SystemExit(f"unexpected boundary paragraph: {end_para.text!r}")

    for offset, (b, r) in enumerate(REWRITES):
        replace_para(doc.paragraphs[start_idx + offset], b, r)

    try:
        doc.save(str(DOC))
        print(f"SAVED {DOC}")
    except PermissionError:
        alt = DOC.with_name(DOC.stem + "_polished.docx")
        doc.save(str(alt))
        print(f"LOCKED; saved {alt}")


if __name__ == "__main__":
    main()
