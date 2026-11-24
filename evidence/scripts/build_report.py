#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Lab 5 Word report in the style of Labs 1–4."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parents[2]
EV = BASE / "evidence"
SHOTS = EV / "shots"
CONSOLE = EV / "console"
SESS = CONSOLE / "sessions"
OUT = BASE / "Ашомка_Андрій_ІМ-34_ЛР5.docx"
OUT_ALT = BASE / "Ашомка_Андрій_ІМ-34_ЛР5_sessions.docx"

COLOR = RGBColor(0x1F, 0x29, 0x37)


def set_run_font(run, *, bold=False, size=12, name="Times New Roman"):
    run.bold = bold
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = COLOR
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)
    rFonts.set(qn("w:cs"), name)


def add_para(doc, text="", *, bold=False, center=False, space_before=0, space_after=6, first_line=True, size=12):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if first_line and text and not center:
        pf.first_line_indent = Cm(1.25)
    else:
        pf.first_line_indent = Cm(0)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if text:
        run = p.add_run(text)
        set_run_font(run, bold=bold, size=size)
    return p


def add_heading(doc, text):
    return add_para(doc, text, bold=True, first_line=False, space_before=14, space_after=6)


def add_sub(doc, text):
    return add_para(doc, text, bold=True, first_line=False, space_before=10, space_after=4)


def add_label(doc, text):
    return add_para(doc, text, first_line=False, space_before=4, space_after=2)


def add_session(doc, text_or_path, *, label="Вивід консолі:", max_chars=12000):
    """Insert a Lab4-style single-cell table with prompt+command+output."""
    add_label(doc, label)
    if isinstance(text_or_path, Path):
        body = read(text_or_path)
    else:
        body = sanitize(str(text_or_path))
    body = body.strip()
    if len(body) > max_chars:
        body = body[:max_chars] + "\n… [скорочено]"
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(body)
    set_run_font(run, size=9, name="Consolas")
    doc.add_paragraph()


def add_shot(doc, path: Path, width_cm=16.0):
    add_label(doc, "Знімок інтерфейсу:")
    if not path.exists():
        add_para(doc, f"[немає файлу {path.name}]", first_line=False)
        return
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))


def add_interp(doc, text):
    add_para(doc, "Інтерпретація: " + text, first_line=True, space_after=8)


def sanitize(text: str) -> str:
    # Word/XML rejects most C0 control chars except tab/newline/CR
    return "".join(ch for ch in text if ch in "\t\n\r" or ord(ch) >= 32)


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return sanitize(path.read_text(encoding="utf-8", errors="replace"))


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(h)
        set_run_font(run, bold=True, size=10)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            set_run_font(run, size=9)
    doc.add_paragraph()


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)
    sec.left_margin = Cm(2.5)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.font.color.rgb = COLOR
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(f"w:{a}"), "Times New Roman")

    # --- Title page ---
    for _ in range(4):
        add_para(doc, "", first_line=False)
    add_para(doc, "Міністерство освіти і науки України", center=True, first_line=False)
    add_para(doc, "Національний технічний університет України", center=True, first_line=False)
    add_para(doc, "«Київський політехнічний інститут імені Ігоря Сікорського»", center=True, first_line=False)
    add_para(doc, "", first_line=False)
    add_para(doc, "Лабораторна робота №5", center=True, first_line=False, bold=True, space_before=24)
    add_para(doc, "з дисципліни", center=True, first_line=False)
    add_para(doc, "«Сучасні інженерні мережеві технології»", center=True, first_line=False, bold=True)
    add_para(doc, "", first_line=False)
    add_para(
        doc,
        "Тема: Аналіз інцидентів інформаційної безпеки. Виявлення сканування та DoS-активності "
        "в дампі мережевого трафіку засобами Wireshark і системи виявлення вторгнень Suricata",
        center=True,
        first_line=False,
        space_before=12,
    )
    add_para(doc, "", first_line=False)
    add_para(doc, "Виконав:\t\t\t\tПеревірив:", first_line=False, space_before=36)
    add_para(doc, "студент групи ІМ-34\t\t\tМельник Назар Андрійович", first_line=False)
    add_para(doc, "Ашомка Андрій Петрович", first_line=False)
    add_para(doc, "", first_line=False)
    add_para(doc, "Київ 2026", center=True, first_line=False, space_before=48)
    doc.add_page_break()

    # --- Goal ---
    add_heading(doc, "Мета роботи")
    add_para(
        doc,
        "Метою роботи є набуття практичних навичок розслідування мережевого інциденту за готовим "
        "дампом трафіку: встановлення нормальної поведінки мережі, виявлення розвідки, сканування "
        "портів і DoS-активності у Wireshark/tshark, перевірка дампу Suricata, зіставлення ручного "
        "й автоматичного аналізу та підготовка технічного звіту.",
    )

    add_heading(doc, "Завдання")
    tasks = [
        "Підготувати середовище (Wireshark/tshark, Suricata 7.x, ET Open), зафіксувати версії, перевірити SHA-256 і capinfos.",
        "Скласти карту мережі за дампом і обґрунтувати ролі вузлів.",
        "Встановити базову лінію нормального трафіку та позначити відхилення на графіку інтенсивності.",
        "Виявити розвідку вузлів (тип, джерело, межі, відповіді).",
        "Виявити сканування портів і визначити його тип за ознаками на рівні пакетів.",
        "Виявити DoS-атаку, виміряти інтенсивність, оцінити підробленість адрес джерел.",
        "Оцінити вплив на легітимних клієнтів.",
        "Перевірити дамп Suricata (ET Open) і зіставити сповіщення з ручним аналізом; порівняти EXTERNAL_NET.",
        "Автоматизувати щонайменше два підрахунки (tshark/Python).",
        "Скласти хронологію, таблицю IoC і висновок для керівництва.",
        "Високий рівень: три власні правила Suricata з порогами; розширення (а) — Python-розслідування у JSON.",
    ]
    for i, t in enumerate(tasks, 1):
        add_para(doc, f"{i}. {t}", first_line=False, space_after=2)

    add_heading(doc, "Результати виконання")
    add_para(
        doc,
        "Варіант 02. Дамп lr5_v02.pcap. Матеріали пункту 6.2 розміщено в каталозі lab5/evidence "
        "(дамп до архіву не додається).",
        first_line=True,
    )

    # 5.3.1 Environment
    add_sub(doc, "5.3.1. Опис середовища")
    add_para(
        doc,
        "ОС: Windows 10 (build 26300) з WSL Ubuntu 24.04. Wireshark/tshark 4.6.10 "
        "(C:\\Program Files\\Wireshark). Suricata 7.0.8 у контейнері jasonish/suricata:7.0.8 "
        "(digest sha256:89b300fb5d00f182359a1305543e828a804ede7f1685e75b05f607f7372428c6). "
        "Набір правил ET Open завантажено suricata-update 2026-11-21 (для suricata-7.0.8; "
        "69545 правил, увімкнено 53572). HOME_NET=[10.42.48.0/24]. Варіант 02.",
        first_line=True,
    )
    add_session(doc, SESS / "01-env-capinfos.txt", label="Вивід консолі (WSL: sha256sum, capinfos, версії):")
    add_interp(
        doc,
        "Дамп містить 64343 пакети за ~598.7 с. Межі в UTC з frame.time_utc: "
        "2026-11-03 09:00:00–09:09:58. "
        "SHA-256 = 7144312da9c0760b7ab64cd07f60e3baff5b6b7aa6508fb51327965507a52e46. "
        "Файл SHA256SUMS з Classroom у робочій папці відсутній, тому звірка з офіційним списком "
        "виконана за обчисленою сумою, зафіксованою у звіті. tshark/capinfos доступні як короткі команди "
        "(Windows PATH + обгортки ~/bin у WSL). Suricata 7.0.8 — у Docker.",
    )

    # 5.3.2 Map
    add_sub(doc, "5.3.2. Карта мережі")
    add_para(
        doc,
        "Команди tshark у WSL і Statistics → Protocol Hierarchy / Endpoints у Wireshark.",
        first_line=False,
    )
    add_session(doc, SESS / "02-map-stats.txt", label="Вивід консолі (io,phs / endpoints,ip / conv,ip):")
    add_shot(doc, SHOTS / "ws-proto-hierarchy.png", 15.5)
    add_shot(doc, SHOTS / "ws-endpoints.png", 15.5)
    add_shot(doc, SHOTS / "network-map.png", 15.0)
    add_interp(
        doc,
        "Усі внутрішні адреси в таблиці Endpoints належать до підмережі 10.42.48.0/24. "
        "Нижче наведено обґрунтування ролі кожного вузла на основі статистики та фільтрів із дампу lr5_v02.pcap.",
    )
    add_para(
        doc,
        "Вебсервер 10.42.48.18:80 (shop.lab.local). У виводі tshark -q -z endpoints,ip ця адреса має "
        "найбільший обсяг трафіку (63587 пакетів, 5693 kB), а в Conversations (conv,ip) більшість "
        "найоб’ємніших розмов відбувається саме за її участю. За фільтром http.request видно звернення "
        "на TCP-порт 80 із заголовком Host: shop.lab.local, що додатково підтверджується A-записом DNS "
        "(shop.lab.local → 10.42.48.18). Отже, 10.42.48.18 — основний вебсервіс, на недоступність "
        "якого надійшла скарга.",
        first_line=True,
    )
    add_para(
        doc,
        "DNS-сервер 10.42.48.2. У Protocol Hierarchy зафіксовано DNS-трафік, а в Endpoints вузол .2 "
        "має помірну кількість пакетів. Команда tshark -Y \"dns && ip.addr==10.42.48.2\" -T fields … "
        "показує, що внутрішні клієнти надсилають DNS-запити саме на .2, а у відповідь отримують "
        "запис A = 10.42.48.18 для shop.lab.local. Крім того, у conv,ip видно обмін 10.42.48.2 ↔ 9.9.9.9: "
        "зовнішні доменні імена локальний DNS-сервер пересилає на публічний рекурсивний резолвер 9.9.9.9 (Quad9).",
        first_line=True,
    )
    add_para(
        doc,
        "Шлюз 10.42.48.1 (MAC 02:9e:28:0f:b4:09). У статистиці IPv4 Endpoints на адресу .1 припадає "
        "лише два пакети (ICMP під час розвідки), оскільки до шлюза майже не звертаються як до кінцевої "
        "служби — транзитний трафік адресований зовнішнім IP. Його роль підтверджується на канальному рівні: "
        "фільтр arp && arp.src.proto_ipv4 == 10.42.48.1 у Wireshark повертає ARP-відповіді з MAC-адресою "
        "02:9e:28:0f:b4:09, і саме цей MAC фігурує в кадрах до/від зовнішніх вузлів (9.9.9.9, джерела "
        "HTTP flood). У цій мережі .1 виконує роль маршрутизатора сегмента (default gateway), а не проксі "
        "перед вебсервером: локальні клієнти звертаються до .18 напряму.",
        first_line=True,
    )
    add_para(
        doc,
        "Легітимні клієнти (.38, .42, .43, .51, .56, .59, .88). Це сім внутрішніх адрес із рівномірним "
        "помірним обсягом трафіку в Endpoints та тривалими сесіями з .18 у conv,ip. За фільтром "
        "http.request && ip.src==10.42.48.0/24 && ip.dst==10.42.48.18 видно звичайні GET-запити на "
        "/, /health, /api/* і /static/* із заголовком Host: shop.lab.local протягом майже всього часу "
        "захоплення. Жоден із цих вузлів не здійснює ARP-обхід і не надсилає масових SYN на різні порти, "
        "тому їх віднесено до штатних клієнтів сервісу.",
        first_line=True,
    )
    add_para(
        doc,
        "Внутрішній атакувальник 10.42.48.126 (розвідка та сканування). Вузол розташований у тій самій "
        "підмережі, що й сервер (відповідно до умови завдання щодо внутрішнього джерела в HOME_NET). "
        "У Endpoints помітний підвищений обсяг його трафіку, а фільтри "
        "arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126 та icmp.type==8 && ip.src==10.42.48.126 "
        "виявляють масовий ARP-обхід і ICMP-опитування живих хостів. Далі фільтр "
        "ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0 фіксує SYN-сканування 1029 портів "
        "вебсервера .18 (розмір вікна 1024), що також виводить .126 у лідери за підрахунком SYN без ACK.",
        first_line=True,
    )
    add_para(
        doc,
        "Зовнішні джерела HTTP flood (8 адрес поза 10.42.48.0/24). У таблицях Endpoints і Conversations "
        "одразу після .18 за обсягом ідуть зовнішні адреси (зокрема 54.85.25.140, 168.2.105.253 тощо). "
        "Фільтр http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24) виділяє 6160 запитів "
        "GET /?<випадкове> у проміжку 09:06:22–09:06:59 UTC із восьми унікальних зовнішніх IP. "
        "Трафік надходить у сегмент через шлюз і становить окремий етап DoS-атаки, незалежний від "
        "внутрішнього сканера .126.",
        first_line=True,
        space_after=6,
    )
    add_para(
        doc,
        "Нижче наведено команду tshark у PowerShell, якою було додатково зафіксовано роль DNS-сервера "
        "10.42.48.2 та прив’язку імені shop.lab.local до 10.42.48.18 (збережено у файлі "
        "evidence/console/dns-sample.txt). Змінні $pcap і $out задають шляхи до дампу та каталогу "
        "evidence, а $env:TZ = \"UTC\" забезпечує узгодження часових позначок із UTC у звіті.",
        first_line=True,
    )
    add_session(
        doc,
        SESS / "02b-dns-sample.txt",
        label="Вивід консолі (PowerShell: DNS за участю 10.42.48.2 → dns-sample.txt):",
    )
    add_para(
        doc,
        "Пояснення прапорців tshark у цій команді: "
        "-r — читати готовий дамп (не live-захоплення); "
        "-Y \"dns && ip.addr==10.42.48.2\" — display-фільтр: лише DNS-пакети за участю DNS-сервера сегмента "
        "(так підтверджуємо його роль і бачимо імена, які він обслуговує); "
        "-T fields — виводити окремі поля замість повного розбору пакета; "
        "-e frame.time_utc / -e ip.src / -e ip.dst / -e dns.qry.name / -e dns.a — колонки: час UTC, "
        "адреси, запитуване ім’я та A-запис у відповіді (у чистому запиті dns.a порожній); "
        "2>&1 — об’єднати stderr із stdout у PowerShell; "
        "Select-Object -First 15 — коротка вибірка перших 15 рядків для evidence; "
        "Set-Content — записати результат у dns-sample.txt. "
        "У виводі видно пари запит/відповідь: клієнти питають shop.lab.local у 10.42.48.2, "
        "відповідь містить A=10.42.48.18; рядок із time.example.net — інший DNS-запит того ж сервера "
        "у тій самій вибірці «перших 15».",
        first_line=True,
        space_after=8,
    )

    # 5.3.3 Baseline
    add_sub(doc, "5.3.3. Базова лінія нормального трафіку")
    add_para(
        doc,
        "До атак легітимні клієнти відкривають ~60–80 нових TCP-з’єднань на хвилину до :80 "
        "(~1–2 SYN/с сумарно), HTTP GET / /health /api/* /status з Host shop.lab.local, "
        "коди 200, типовий http.time ≈ 0.011 с. Протоколи базової лінії: TCP/HTTP, DNS, NTP.",
        first_line=True,
    )
    add_session(doc, SESS / "03-io-stat.txt", label="Вивід консолі (io,stat,10 та SYN за 1 с):")
    add_shot(doc, SHOTS / "ws-io-graphs.png", 15.5)
    add_interp(
        doc,
        "На графіку інтенсивності видно три відхилення: ARP/ICMP ~09:01:44, SYN-скан ~09:02:18 "
        "та HTTP flood ~09:06:22–09:06:59. Поза цими вікнами темп близький до базової лінії.",
    )

    # Recon
    add_sub(doc, "5.3.3 (п.4). Розвідка вузлів")
    add_para(
        doc,
        "Фільтри: arp.opcode == 1 && arp.src.proto_ipv4 == 10.42.48.126; "
        "icmp.type == 8 && ip.src == 10.42.48.126.",
        first_line=False,
    )
    add_session(doc, SESS / "04-recon.txt", label="Вивід консолі (ARP/ICMP розвідка):")
    add_shot(doc, SHOTS / "ws-arp-recon.png", 15.5)
    add_shot(doc, SHOTS / "ws-icmp-recon.png", 15.5)
    add_interp(
        doc,
        "Тип: ARP-обхід з подальшим ICMP echo request. Джерело 10.42.48.126. "
        "ARP: 253 who-has у 09:01:44.528–09:01:46.124 UTC. ICMP: 10 адрес "
        "(.1 .2 .18 .38 .42 .43 .51 .56 .59 .88) у 09:01:44.529–09:01:45.081 UTC; усі відповіли echo-reply. "
        "У локальному сегменті будь-яке IP-опитування починається з ARP, бо без MAC L2-кадру не зібрати.",
    )

    # Port scan
    add_sub(doc, "5.3.3 (п.5). Сканування портів")
    add_para(
        doc,
        "Фільтри: ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0; "
        "відкриті — SYN+ACK від цілі; закриті — RST від цілі.",
        first_line=False,
    )
    add_session(doc, SESS / "05-scan.txt", label="Вивід консолі (SYN-скан, відкриті порти, потік :80):")
    add_shot(doc, SHOTS / "ws-syn-scan.png", 15.5)
    add_shot(doc, SHOTS / "ws-open-ports.png", 15.5)
    add_interp(
        doc,
        "Джерело 10.42.48.126 → ціль 10.42.48.18; 09:02:18.581–09:02:20.063 UTC; 1029 унікальних портів. "
        "Відкриті: 21, 22, 80; закриті: 1026 (RST). Тип — SYN-сканування (half-open): SYN з window=1024, "
        "на відкритому порту після SYN-ACK сканер одразу шле RST і не завершує handshake. "
        "Це відрізняє його від connect-сканування з повним з’єднанням.",
    )

    # DoS
    add_sub(doc, "5.3.3 (п.6). DoS-атака")
    add_para(
        doc,
        "Фільтр: http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24). "
        "Інтенсивність: пік за 1 с і середнє = кількість запитів / тривалість вікна.",
        first_line=False,
    )
    add_session(doc, SESS / "06-dos.txt", label="Вивід консолі (HTTP flood, джерела, handshake):")
    add_shot(doc, SHOTS / "ws-http-flood.png", 15.5)
    add_interp(
        doc,
        "Тип — HTTP flood (L7). Ціль 10.42.48.18:80 (shop.lab.local). Вікно 09:06:22.123–09:06:59.402 UTC "
        "(~37.28 с). 6160 GET /?<випадкове>; 8 унікальних зовнішніх джерел. Пік ≈ 189 req/s (09:06:24), "
        "середнє ≈ 165.24 req/s. Handshake завершується (SYN→SYN-ACK→ACK+HTTP), "
        "адреси джерел не підроблені (трафік через MAC шлюзу 02:9e:28:0f:b4:09, TTL≈109).",
    )

    # Impact
    add_sub(doc, "5.3.3 (п.7). Вплив на легітимних клієнтів")
    add_session(doc, SESS / "07-impact.txt", label="Вивід консолі (коди/час відповіді під час flood, HTTP 503):")
    add_shot(doc, SHOTS / "ws-impact.png", 15.5)
    add_interp(
        doc,
        "До атаки: HTTP 200, http.time ≈ 0.011 с. Під час flood: частина відповідей 503, "
        "середній час відповіді ≈ 0.45 с (до ~0.89 с). Після 09:06:59 знову лише 200 і ~0.011 с. "
        "Повторні передачі майже не зросли (1 до / 1 під час). Вплив істотний на час відповіді й коди, "
        "але закінчився разом з атакою — сервіс відновився без залишкового відмовлення.",
    )

    # Suricata
    add_sub(doc, "5.3.3 (п.8). Suricata (ET Open)")
    add_para(
        doc,
        "Команда: TZ=UTC suricata --runmode single -r lr5_v02.pcap -l out -k none "
        "(образ jasonish/suricata:7.0.8). Другий прогін з --set vars.address-groups.EXTERNAL_NET=any.",
        first_line=False,
    )
    add_session(doc, SESS / "09-suricata-default.txt", label="Вивід консолі (Suricata ET Open, EXTERNAL_NET=!$HOME_NET):")
    add_session(doc, SESS / "10-suricata-external-any.txt", label="Вивід консолі (Suricata ET Open, EXTERNAL_NET=any):")
    add_interp(
        doc,
        "ET Open у обох прогонах дав сповіщення лише сигнатури WordPress posts-layout — "
        "хибні/малоінформативні спрацювання на випадкові URI flood. Розвідку, SYN-скан і HTTP flood "
        "як DoS набір не класифікував. Різниця EXTERNAL_NET для цього дампу не змінила зміст alerts, "
        "бо відповідні ET SCAN/ICMP правила або не збіглися з відбитком, або відсутні у увімкненому наборі; "
        "проте HOME_NET=[10.42.48.0/24] критичний: атакувальник внутрішній, тож правила "
        "$EXTERNAL_NET → $HOME_NET його принципово ігнорують, доки EXTERNAL_NET≠any. "
        "Саме тому для внутрішнього сканера потрібні власні правила / корекція змінних.",
    )

    # Automation
    add_sub(doc, "5.3.3 (п.9). Автоматизація")
    add_para(
        doc,
        "1) tshark/python: SYN без ACK за джерелом. "
        "2) summarize_eve.py — зведення alerts з eve.json.",
        first_line=False,
    )
    add_session(doc, SESS / "08-syn-by-src.txt", label="Вивід консолі (підрахунок SYN за джерелом):")
    add_interp(
        doc,
        "Автоматичний підрахунок відтворює ручний висновок: лідери SYN — flood-джерела та 10.42.48.126 (сканер). "
        "summarize_eve.py зводить сигнатури однією командою (див. сесії Suricata вище).",
    )

    # Comparison table 5.3.4
    add_sub(doc, "5.3.4. Зіставлення ручного аналізу і Suricata")
    add_table(
        doc,
        ["Подія", "Вручну (фільтр/графік)", "Suricata ET Open", "Висновок"],
        [
            [
                "Розвідка вузлів",
                "ARP+ICMP від .126, 09:01:44",
                "Не виявила",
                "ARP/швидкий ICMP sweep поза ET Open",
            ],
            [
                "Сканування портів",
                "SYN window=1024, RST після SYN-ACK",
                "Не виявила",
                "Внутрішнє джерело; потрібні власні правила",
            ],
            [
                "DoS HTTP flood",
                "6160 GET /?n, пік 189 rps",
                "WordPress FP (див. eve summary)",
                "Flood не класифіковано; FP за URI",
            ],
            [
                "Вплив на клієнтів",
                "503 + ↑ http.time під час flood",
                "Немає окремої сигнатури впливу",
                "Вплив видно лише ручним аналізом",
            ],
            [
                "Хибні сповіщення",
                "—",
                "ET WordPress posts-layout",
                "Малоінформативно для цього інциденту",
            ],
        ],
    )

    # Chronology 5.3.5
    add_sub(doc, "5.3.5. Хронологія інциденту (UTC)")
    add_table(
        doc,
        ["Час (UTC)", "Подія"],
        [
            ["2026-11-03 09:00:00", "Початок дампу; нормальний трафік клієнтів → shop.lab.local"],
            ["2026-11-03 09:01:44–09:01:46", "ARP-обхід з 10.42.48.126 (253 адреси)"],
            ["2026-11-03 09:01:44–09:01:45", "ICMP echo до 10 живих вузлів"],
            ["2026-11-03 09:02:18–09:02:20", "SYN-сканування 10.42.48.18 (1029 портів; відкриті 21/22/80)"],
            ["2026-11-03 09:06:22–09:06:59", "HTTP flood з 8 зовнішніх адрес (пік ~189 req/s)"],
            ["2026-11-03 09:06:22–09:06:59", "Вплив: 503 і зростання часу відповіді у легітимних клієнтів"],
            ["2026-11-03 09:07:00+", "Відновлення базової лінії (HTTP 200, ~11 мс)"],
            ["2026-11-03 09:09:58", "Кінець дампу"],
        ],
    )

    # IoC 5.3.6
    add_sub(doc, "5.3.6. Індикатори компрометації (IoC)")
    add_table(
        doc,
        ["Тип індикатора", "Значення", "Часові межі (UTC)", "Чим підтверджено"],
        [
            [
                "Адреса джерела розвідки і сканування",
                "10.42.48.126 (MAC 02:94:d0:09:fb:ff)",
                "09:01:44–09:02:20",
                "ARP/ICMP/SYN фільтри; window=1024",
            ],
            [
                "Атакований вузол і сервіси",
                "10.42.48.18:80 (shop.lab.local); також :21,:22 відкриті",
                "скан 09:02:18; flood 09:06:22",
                "SYN-ACK/HTTP Host",
            ],
            [
                "Джерела DoS",
                "8 адрес: 54.85.25.140, 168.2.105.253, 190.187.3.200, 102.254.200.172, 36.115.221.91, 66.25.118.46, 168.96.108.184, 13.65.227.72",
                "09:06:22–09:06:59",
                "http.request; завершений handshake",
            ],
            [
                "Сигнатури IDS",
                "ET WordPress posts-layout (FP); власні LAB5 sid 1000001–1000003",
                "див. eve.json",
                "eve.json / fast.log",
            ],
        ],
    )

    # Management conclusion 5.3.7
    add_sub(doc, "5.3.7. Висновок для керівництва")
    add_para(
        doc,
        "Протягом десяти хвилин внутрішній вузол 10.42.48.126 спочатку знайшов живі хости в сегменті, "
        "потім швидко просканував вебсервер shop.lab.local і виявив відкриті служби. Невдовзі на цей "
        "вебсервер з восьми зовнішніх адрес пішов шквал HTTP-запитів. У піку сервіс відповідав повільніше "
        "й іноді кодом «сервіс тимчасово недоступний», тож користувачі відчули деградацію. Після закінчення "
        "шквалу робота відновилась. Рекомендовано: ізолювати/перевірити вузол 10.42.48.126; увімкнути "
        "обмеження частоти запитів на вебсервері та WAF/rate-limit на периметрі; закрити зайві порти "
        "21/22 якщо вони не потрібні; налаштувати IDS з урахуванням внутрішніх джерел і сповіщеннями "
        "на сплеск HTTP до критичного сервісу.",
        first_line=True,
    )

    # High level 5.3.8
    add_sub(doc, "5.3.8. Високий рівень: власні правила та розширення (а)")
    add_para(doc, "Файл правил: evidence/rules/local.rules", first_line=False)
    add_session(doc, SESS / "11-suricata-custom.txt", label="Вивід консолі (власні правила + cat local.rules):")
    add_para(
        doc,
        "Обґрунтування порогів: значення підібрано відносно базової лінії. Для SYN-сканування — "
        "50 пакетів за 5 с (проти 1–2 SYN/с у легітимних клієнтів) із умовою window:1024, щоб не "
        "плутати зі SYN HTTP-flood (window 64240). Для HTTP flood — 80 запитів за 2 с (проти ~1–2 req/с "
        "фону); URI-шаблон pcre:\"/\\/\\?[A-Za-z0-9]+/\" ловить GET /?<випадковий рядок> з цифр і/або "
        "літер (у цьому дампі — цифри; літери теж покриті, щоб атакувальник не обійшов правило "
        "простою заміною алфавіту). Для ICMP-розвідки — 5 echo за 2 с за майже нульового ICMP у нормі.",
        first_line=True,
    )
    add_interp(
        doc,
        "Власні правила спрацювали на атаки (.126 для ICMP/SYN; зовнішні джерела для HTTP flood) "
        "і не спрацювали на легітимних клієнтів .38–.88. Події, які сигнатура Suricata принципово "
        "погано бачить без спеціальних правил: чистий ARP-обхід (L2), оцінка впливу на користувачів "
        "(коди/латентність), семантика «це саме HTTP flood, а не сканер WordPress».",
    )
    add_para(
        doc,
        "Розширення (а): python evidence/scripts/investigate.py lr5_v02.pcap → incident.json.",
        first_line=False,
    )
    add_session(doc, SESS / "12-investigate.txt", label="Вивід консолі (investigate.py → incident.json):")
    add_interp(
        doc,
        "Скрипт автоматично визначив джерело/межі сканування (SYN scan .126→.18) і тип/межі DoS "
        "(HTTP flood, 8 джерел, пік/середнє), що збігається з ручним аналізом у межах секунди.",
    )

    # Conclusions
    add_heading(doc, "Висновки")
    add_para(
        doc,
        "Ручний аналіз Wireshark/tshark повністю відновив хронологію: розвідка → SYN-скан → HTTP flood → "
        "деградація сервісу → відновлення. Сигнатурна IDS (ET Open) швидко відфільтрувала дамп, але "
        "для цього варіанта майже не дала змістовних alerts: внутрішній атакувальник і відсутність "
        "релевантних сигнатур призвели до пропусків; єдині сповіщення — хибні WordPress. Власні порогові "
        "правила залежать від порогів відносно базової лінії: занижені дають шум, завищені — пропуск. "
        "IDS лише виявляє й сповіщає; IPS може блокувати (drop) у розрізі трафіку. У стенді ЛР1 IDS "
        "доцільно ставити на дзеркало/SPAN біля proxy або на хост-датчик сегмента; IPS — inline перед "
        "Nginx proxy (або в network namespace сервісу), щоб різати скан/flood до app, не ламаючи легітимний "
        "шлях клієнт→proxy→app→Redis.",
        first_line=True,
    )

    add_heading(doc, "Підписи")
    add_para(doc, "Виконавець: Ашомка Андрій Петрович, група ІМ-34", first_line=False)
    add_para(doc, "Роботу прийняв: Мельник Назар Андрійович", first_line=False)
    add_para(doc, "Дата: ____________________", first_line=False)

    try:
        doc.save(OUT)
        print("saved", OUT)
    except PermissionError:
        doc.save(OUT_ALT)
        print("locked; saved", OUT_ALT)


if __name__ == "__main__":
    build()
