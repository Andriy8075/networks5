#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polish all remaining text sections of the Lab 5 Word report for naturalness and readability."""
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

BASE = Path(__file__).resolve().parents[2]
DOC = BASE / "Ашомка_Андрій_ІМ-34_ЛР5.docx"
COLOR = RGBColor(0x1F, 0x29, 0x37)


def set_run_font(run, *, bold=False, size=12, name="Times New Roman"):
    run.bold = bold
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = COLOR
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(f"w:{a}"), name)


def replace_para(p, bold_prefix: str, rest: str, *, first_line=True, space_after=6):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.paragraph_format.first_line_indent = Cm(1.25 if first_line else 0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        set_run_font(r1, bold=True)
    if rest:
        r2 = p.add_run(rest)
        set_run_font(r2, bold=False)


def insert_para_after(anchor, bold_prefix: str, rest: str, *, first_line=True, space_after=6):
    new_p = OxmlElement("w:p")
    anchor._p.addnext(new_p)
    p = Paragraph(new_p, anchor._parent)
    replace_para(p, bold_prefix, rest, first_line=first_line, space_after=space_after)
    return p


def set_cell_text(cell, text: str, *, bold=False, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    set_run_font(run, bold=bold, size=size)


def find_para(doc, prefix: str):
    for p in doc.paragraphs:
        if p.text.startswith(prefix):
            return p
    return None


def main():
    doc = Document(str(DOC))

    # --- Мета роботи ---
    p = find_para(doc, "Метою роботи є")
    if p:
        replace_para(
            p,
            "",
            "Метою роботи є набуття практичних навичок розслідування мережевого інциденту за готовим "
            "дампом трафіку: визначення базової лінії нормальної роботи мережі, виявлення розвідки, "
            "сканування портів і DoS-атаки у Wireshark та tshark, перевірки дампу системою виявлення "
            "вторгнень Suricata, зіставлення ручного й автоматизованого аналізу та підготовки "
            "технічного звіту.",
            first_line=True,
            space_after=6,
        )

    # --- 5.3.1 Опис середовища ---
    p = find_para(doc, "ОС: Windows 10")
    if p:
        replace_para(
            p,
            "",
            "Аналіз виконано в операційній системі Windows 10 (build 26300) із використанням WSL "
            "Ubuntu 24.04. Для розбору пакетів застосовано Wireshark і tshark версії 4.6.10 "
            "(каталог C:\\Program Files\\Wireshark). Систему виявлення вторгнень Suricata 7.0.8 "
            "розгорнуто в Docker-контейнері на основі образу jasonish/suricata:7.0.8 "
            "(digest sha256:89b300fb5d00f182359a1305543e828a804ede7f1685e75b05f607f7372428c6). "
            "Набір правил ET Open завантажено за допомогою suricata-update 2026-11-21 для гілки "
            "suricata-7.0.8 (усього 69545 правил, із них увімкнено 53572). У конфігурації задано "
            "HOME_NET = [10.42.48.0/24]. Досліджуваний дамп відповідає варіанту 02 (lr5_v02.pcap).",
            first_line=True,
            space_after=6,
        )

    p = find_para(doc, "Інтерпретація: Дамп містить 64343")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "Дамп містить 64343 пакети загальною тривалістю близько 598,7 с. За полем frame.time_utc "
            "захоплення охоплює проміжок 2026-11-03 09:00:00–09:09:58 UTC. Обчислена контрольна сума "
            "SHA-256 становить 7144312da9c0760b7ab64cd07f60e3baff5b6b7aa6508fb51327965507a52e46, "
            "версія tshark — 4.6.10.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.2 Карта мережі (вступний рядок) ---
    p = find_para(doc, "Команди tshark у WSL і Statistics")
    if p:
        replace_para(
            p,
            "",
            "Для побудови карти мережі використано статистику tshark у WSL та відповідні розділи "
            "Wireshark (Statistics → Protocol Hierarchy, Endpoints і Conversations).",
            first_line=True,
            space_after=6,
        )

    # --- 5.3.3 Базова лінія ---
    p = find_para(doc, "До атак легітимні клієнти відкривають")
    if p:
        replace_para(
            p,
            "",
            "У штатному режимі до початку атак легітимні клієнти відкривають приблизно 60–80 нових "
            "TCP-з’єднань за хвилину до порту 80 (сумарно 1–2 SYN/с). Вони надсилають звичайні запити "
            "HTTP GET на маршрути /, /health, /api/* та /status із заголовком Host: shop.lab.local, "
            "отримують відповіді з кодом 200, а типовий час відповіді вебсервера (http.time) становить "
            "близько 0,011 с. Базовий фон трафіку формують протоколи TCP/HTTP, DNS і NTP.",
            first_line=True,
            space_after=6,
        )

    p = find_para(doc, "Інтерпретація: На графіку інтенсивності")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "На графіку інтенсивності чітко виділяються три періоди відхилення від базової лінії: "
            "розвідка ARP/ICMP близько 09:01:44 UTC, сплеск SYN-сканування близько 09:02:18 UTC та "
            "тривалий пік HTTP flood у проміжку 09:06:22–09:06:59 UTC. Поза цими інтервалами "
            "інтенсивність трафіку відповідає нормальному рівню.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.3 (п.4) Розвідка вузлів ---
    p = find_para(doc, "Фільтри: arp.opcode == 1")
    if p:
        replace_para(
            p,
            "Застосовані фільтри: ",
            "arp.opcode == 1 && arp.src.proto_ipv4 == 10.42.48.126 (ARP-запити) та "
            "icmp.type == 8 && ip.src == 10.42.48.126 (ICMP echo request).",
            first_line=False,
            space_after=4,
        )

    p = find_para(doc, "Інтерпретація: Тип: ARP-обхід")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "Виявлено комбіновану розвідку — ARP-обхід сегмента з подальшим ICMP-опитуванням "
            "знайдених вузлів. Джерелом є внутрішній хост 10.42.48.126. У проміжку "
            "09:01:44.528–09:01:46.124 UTC він надіслав 253 ARP-запити (who-has), а в інтервалі "
            "09:01:44.529–09:01:45.081 UTC перевірив 10 активних адрес (.1, .2, .18, .38, .42, .43, "
            ".51, .56, .59, .88) за допомогою ICMP echo request — усі десять відповіли echo-reply. "
            "У локальному L2-сегменті будь-яке опитування IP-адрес починається саме з ARP, оскільки "
            "без MAC-адреси отримувача неможливо сформувати Ethernet-кадр.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.3 (п.5) Сканування портів ---
    p = find_para(doc, "Фільтри: ip.src==10.42.48.126")
    if p:
        replace_para(
            p,
            "Застосовані фільтри: ",
            "ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0 (усі спроби підключення); "
            "SYN+ACK від цілі — для виявлення відкритих портів; RST від цілі — для закритих портів.",
            first_line=False,
            space_after=4,
        )

    p = find_para(doc, "Інтерпретація: Джерело 10.42.48.126")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "З вузла 10.42.48.126 на вебсервер 10.42.48.18 у проміжку 09:02:18.581–09:02:20.063 UTC "
            "проведено сканування 1029 унікальних TCP-портів. Відкритими виявилися три порти — 21, 22 "
            "і 80 (сервер відповів SYN-ACK), а решта 1026 портів закриті (відповідь RST). За ознаками "
            "на рівні пакетів це класичне SYN-сканування (half-open): сканер надсилає SYN із малим "
            "розміром вікна (window = 1024), а на відкритому порту одразу після отримання SYN-ACK "
            "обриває спробу пакетом RST, не завершуючи тристороннє рукостискання. Саме це відрізняє "
            "його від connect-сканування з повним встановленням TCP-з’єднання.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.3 (п.6) DoS-атака ---
    p = find_para(doc, "Фільтр: http.request && ip.dst==10.42.48.18")
    if p:
        replace_para(
            p,
            "Застосований фільтр: ",
            "http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24). Пікову інтенсивність "
            "визначено як максимум за 1-секундний інтервал, а середню — як відношення загальної "
            "кількості запитів до тривалості вікна атаки.",
            first_line=False,
            space_after=4,
        )

    p = find_para(doc, "Інтерпретація: Тип — HTTP flood")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "Зафіксовано DoS-атаку прикладного рівня — HTTP flood на вебсервер 10.42.48.18:80 "
            "(shop.lab.local). Атака тривала 37,28 с у проміжку 09:06:22.123–09:06:59.402 UTC: "
            "із восьми унікальних зовнішніх IP-адрес надійшло 6160 запитів GET /?<випадкове_число>. "
            "Пікова інтенсивність сягнула 189 запитів/с (о 09:06:24 UTC), середня — 165,24 запитів/с. "
            "Адреси джерел не є підробленими (не spoofed): кожне джерело повноцінно завершує TCP "
            "handshake (SYN → SYN-ACK → ACK) і лише після цього передає HTTP-запит; у сегмент "
            "пакети заходять через шлюз (MAC 02:9e:28:0f:b4:09, TTL ≈ 109).",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.3 (п.7) Вплив на легітимних клієнтів ---
    p = find_para(doc, "Інтерпретація: До атаки: HTTP 200")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "До початку DoS-атаки всі легітимні клієнти отримували відповіді HTTP 200 із середнім "
            "часом обробки близько 0,011 с. Під час HTTP flood сервіс помітно деградував: частина "
            "запитів повертала код 503 (Service Unavailable), а середній час відповіді зріс до "
            "0,45 с (в окремих випадках — до 0,89 с). Кількість повторних передач TCP майже не "
            "змінилася (1 до атаки та 1 під час неї). Одразу після 09:06:59 UTC робота сервісу "
            "повернулася до норми (лише HTTP 200 і ~0,011 с), тож вплив був відчутним, але "
            "завершився разом з атакою без залишкової відмови.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.3 (п.8) Suricata (ET Open) ---
    p = find_para(doc, "Команда: TZ=UTC suricata")
    if p:
        replace_para(
            p,
            "Команда запуску: ",
            "TZ=UTC suricata --runmode single -r lr5_v02.pcap -l out -k none (у контейнері "
            "jasonish/suricata:7.0.8). Повторний прогін виконано з параметром "
            "--set vars.address-groups.EXTERNAL_NET=any для перевірки впливу змінних мережі.",
            first_line=False,
            space_after=4,
        )

    p = find_para(doc, "Інтерпретація: ET Open у обох прогонах")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "В обох прогонах стандартний набір правил ET Open видав лише сповіщення за сигнатурою "
            "WordPress posts-layout — це хибні (малоінформативні) спрацювання на випадкові параметри "
            "URI під час HTTP flood. Ні розвідку вузлів, ні SYN-сканування, ні саму DoS-атаку набір "
            "не класифікував. Зміна EXTERNAL_NET на any у цьому дампі не додала змістовних сповіщень, "
            "оскільки відповідні правила ET SCAN/ICMP або не збіглися з відбитком сканера, або не "
            "входять до активної частини набору. Водночас коректне налаштування HOME_NET=[10.42.48.0/24] "
            "є принциповим: атакувальник .126 перебуває у внутрішній мережі, тому правила напрямку "
            "$EXTERNAL_NET → $HOME_NET гарантовано його ігнорують, доки EXTERNAL_NET не змінено на any. "
            "Для виявлення таких внутрішніх загроз потрібні власні правила або адаптація змінних IDS.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.3 (п.9) Автоматизація ---
    p = find_para(doc, "1) tshark/python: SYN без ACK")
    if p:
        replace_para(
            p,
            "",
            "Автоматизовано два відтворювані підрахунки: 1) розподіл пакетів SYN без ACK за адресою "
            "джерела (tshark і скрипт count_syn_by_src.py); 2) зведення сповіщень із eve.json "
            "скриптом summarize_eve.py.",
            first_line=True,
            space_after=4,
        )

    p = find_para(doc, "Інтерпретація: Автоматичний підрахунок")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "Автоматичний підрахунок повністю підтверджує висновки ручного аналізу: на перших "
            "позиціях за кількістю SYN-пакетів перебувають вісім зовнішніх джерел HTTP flood та "
            "внутрішній сканер 10.42.48.126. Скрипт summarize_eve.py дозволяє однією командою "
            "звести всі сигнатури з eve.json (результати наведено у сесіях Suricata вище).",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.7 Висновок для керівництва ---
    p = find_para(doc, "Протягом десяти хвилин внутрішній вузол")
    if p:
        replace_para(
            p,
            "",
            "Протягом десятихвилинного вікна спостереження зафіксовано двоетапний інцидент. "
            "Спочатку внутрішній вузол 10.42.48.126 провів розвідку активних хостів у сегменті "
            "та швидко просканував вебсервер shop.lab.local, виявивши відкриті порти 21, 22 і 80. "
            "Невдовзі після цього на вебсервер надійшов шквал HTTP-запитів із восьми зовнішніх адрес "
            "(тривалістю близько 37 секунд). Під час пікового навантаження сервіс відповідав у десятки "
            "разів повільніше та періодично повертав помилку «сервіс тимчасово недоступний» (HTTP 503), "
            "що безпосередньо відчули користувачі. Після припинення атаки робота сервісу повністю "
            "відновилася.",
            first_line=True,
            space_after=6,
        )
        insert_para_after(
            p,
            "Рекомендовані заходи: ",
            "негайно перевірити та за потреби ізолювати внутрішній вузол 10.42.48.126 для з’ясування "
            "причини підозрілої активності; запровадити обмеження частоти запитів (rate limiting) на "
            "вебсервері та WAF на периметрі; закрити або обмежити доступ до портів 21 і 22, якщо вони "
            "не використовуються; оновити політики IDS із урахуванням внутрішніх джерел та додати "
            "сповіщення про аномальні сплески HTTP-запитів до критичних сервісів.",
            first_line=True,
            space_after=8,
        )

    # --- 5.3.8 Високий рівень ---
    p = find_para(doc, "Файл правил: evidence/rules/local.rules")
    if p:
        replace_para(
            p,
            "Файл власних правил: ",
            "evidence/rules/local.rules (сигнатури sid 1000001–1000003).",
            first_line=False,
            space_after=4,
        )

    p = find_para(doc, "Пороги: SYN-скан")
    if p:
        replace_para(
            p,
            "Обґрунтування порогів: ",
            "значення підібрано відносно базової лінії нормального трафіку. Для SYN-сканування задано "
            "поріг 50 пакетів за 5 с (проти 1–2 SYN/с у легітимних клієнтів) із додатковою умовою "
            "window:1024, що дозволяє точно відокремити відбиток сканера від SYN-пакетів HTTP flood "
            "(де розмір вікна становить 64240). Для HTTP flood встановлено поріг 80 запитів за 2 с "
            "(проти ~1–2 запитів/с у фоновому режимі), а для ICMP-розвідки — 5 echo-запитів за 2 с "
            "за майже повної відсутності ICMP у штатній роботі.",
            first_line=True,
            space_after=6,
        )

    p = find_para(doc, "Інтерпретація: Власні правила спрацювали")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "Усі три власні правила спрацювали саме на етапи атаки (вузол .126 для ICMP та SYN-скану; "
            "зовнішні адреси для HTTP flood) і не дали жодного хибного спрацювання на трафік легітимних "
            "клієнтів (.38–.88). Водночас існують аспекти інциденту, які сигнатурні правила Suricata "
            "принципово не охоплюють або фіксують обмежено: чистий ARP-обхід на рівні L2, оцінку "
            "реального впливу на користувачів (зростання затримок і частку відповідей 503), а також "
            "контекстне розрізнення цілеспрямованого HTTP flood від збігу URI з побічною сигнатурою.",
            first_line=True,
            space_after=8,
        )

    p = find_para(doc, "Розширення (а): python evidence/scripts/investigate.py")
    if p:
        replace_para(
            p,
            "Розширення (а) — автоматизоване розслідування: ",
            "скрипт python evidence/scripts/investigate.py lr5_v02.pcap автоматично аналізує дамп "
            "та формує структурований звіт у форматі JSON (evidence/scripts/incident.json).",
            first_line=False,
            space_after=4,
        )

    p = find_para(doc, "Інтерпретація: Скрипт автоматично визначив")
    if p:
        replace_para(
            p,
            "Інтерпретація: ",
            "Скрипт коректно визначив джерело й часові межі сканування (SYN scan із 10.42.48.126 на "
            "10.42.48.18) та характеристики DoS-атаки (HTTP flood із 8 зовнішніх джерел, пікову й "
            "середню інтенсивність). Отримані значення збігаються з результатами ручного аналізу з "
            "точністю до секунди.",
            first_line=True,
            space_after=8,
        )

    # --- Висновки ---
    p = find_para(doc, "Ручний аналіз Wireshark/tshark")
    if p:
        replace_para(
            p,
            "",
            "Ручний аналіз у Wireshark і tshark дозволив повністю відновити перебіг інциденту: "
            "внутрішню розвідку (ARP та ICMP), SYN-сканування портів вебсервера, зовнішній HTTP flood, "
            "тимчасову деградацію сервісу для легітимних клієнтів і подальше відновлення роботи. "
            "Сигнатурна система Suricata зі стандартним набором ET Open швидко опрацювала дамп, "
            "однак для цього варіанта майже не дала змістовних сповіщень: внутрішнє розташування "
            "сканера та відсутність релевантних сигнатур призвели до пропусків, а єдині алерти "
            "виявилися хибними спрацюваннями WordPress. Це підтверджує, що IDS не замінює ручного "
            "розбору пакетів, а її сповіщення потребують критичної перевірки.",
            first_line=True,
            space_after=6,
        )
        p2 = insert_para_after(
            p,
            "",
            "Власні порогові правила Suricata успішно виявили всі три етапи атаки без хибних "
            "спрацювань на легітимний трафік, але їхня якість прямо залежить від коректного підбору "
            "порогів відносно базової лінії: занижені пороги створюють шум, а завищені призводять "
            "до пропуску коротких або менш інтенсивних атак.",
            first_line=True,
            space_after=6,
        )
        insert_para_after(
            p2,
            "",
            "Принципова відмінність між IDS та IPS полягає в реакції на загрозу: IDS працює пасивно "
            "(лише виявляє та сповіщає), тоді як IPS розміщується в розриві трафіку (inline) і може "
            "блокувати небезпечні пакети дією drop. У контексті стенда ЛР1 систему IDS доцільно "
            "підключати пасивно (через дзеркалювання трафіку/SPAN біля проксі або на хост-датчику "
            "сегмента), а IPS — встановлювати inline перед Nginx-проксі (або в мережевому просторі "
            "сервісу), щоб відсікати сканування та flood ще до застосунку, не порушуючи штатний "
            "маршрут клієнт → proxy → app → Redis.",
            first_line=True,
            space_after=8,
        )

    # --- Polish multi-column summary tables (T11, T12, T13) ---
    for tbl in doc.tables:
        if len(tbl.columns) == 4 and tbl.rows[0].cells[0].text.strip() == "Подія":
            # Comparison table 5.3.4
            updates = [
                ("Розвідка вузлів", "ARP + ICMP від .126 (09:01:44 UTC)", "Не виявлено", "ARP та короткий ICMP sweep не покрито ET Open"),
                ("Сканування портів", "SYN (window=1024), RST після SYN-ACK", "Не виявлено", "Внутрішнє джерело; потрібні власні правила"),
                ("DoS (HTTP flood)", "6160 GET /?<n>, пік 189 req/s", "Хибні WordPress (див. eve summary)", "Атаку не класифіковано як DoS; хибні спрацювання за URI"),
                ("Вплив на клієнтів", "HTTP 503 і зростання http.time під час flood", "Окремої сигнатури немає", "Деградацію сервісу видно лише під час ручного аналізу"),
                ("Хибні сповіщення", "—", "ET WordPress posts-layout", "Малоінформативні для цього інциденту"),
            ]
            for ri, row_vals in enumerate(updates, start=1):
                if ri < len(tbl.rows):
                    for ci, val in enumerate(row_vals):
                        set_cell_text(tbl.rows[ri].cells[ci], val, size=9)

        elif len(tbl.columns) == 2 and tbl.rows[0].cells[0].text.strip() == "Час (UTC)":
            # Timeline table 5.3.5
            updates = [
                ("2026-11-03 09:00:00", "Початок дампу; штатний трафік клієнтів до shop.lab.local"),
                ("2026-11-03 09:01:44–09:01:46", "ARP-обхід сегмента з 10.42.48.126 (253 адреси)"),
                ("2026-11-03 09:01:44–09:01:45", "ICMP echo-опитування 10 активних вузлів"),
                ("2026-11-03 09:02:18–09:02:20", "SYN-сканування 10.42.48.18 (1029 портів; відкриті 21, 22, 80)"),
                ("2026-11-03 09:06:22–09:06:59", "HTTP flood із 8 зовнішніх адрес (6160 запитів, пік 189 req/s)"),
                ("2026-11-03 09:06:22–09:06:59", "Вплив на клієнтів: помилки HTTP 503 і зростання часу відповіді"),
                ("2026-11-03 09:07:00+", "Відновлення базової лінії (лише HTTP 200, час відповіді ~11 мс)"),
                ("2026-11-03 09:09:58", "Завершення дампу"),
            ]
            for ri, row_vals in enumerate(updates, start=1):
                if ri < len(tbl.rows):
                    for ci, val in enumerate(row_vals):
                        set_cell_text(tbl.rows[ri].cells[ci], val, size=9)

        elif len(tbl.columns) == 4 and tbl.rows[0].cells[0].text.strip() == "Тип індикатора":
            # IoC table 5.3.6
            updates = [
                ("Джерело розвідки та сканування", "10.42.48.126 (MAC 02:94:d0:09:fb:ff)", "09:01:44–09:02:20", "Фільтри ARP/ICMP/SYN; window = 1024"),
                ("Атакований вузол і сервіси", "10.42.48.18:80 (shop.lab.local); також відкриті :21, :22", "скан 09:02:18; flood 09:06:22", "Відповіді SYN-ACK, заголовок HTTP Host"),
                ("Джерела DoS-атаки", "8 зовнішніх адрес: 54.85.25.140, 168.2.105.253, 190.187.3.200, 102.254.200.172, 36.115.221.91, 66.25.118.46, 168.96.108.184, 13.65.227.72", "09:06:22–09:06:59", "Фільтр http.request; завершений TCP handshake"),
                ("Сигнатури IDS", "ET WordPress posts-layout (хибні); власні LAB5 (sid 1000001–1000003)", "див. eve.json", "Логи eve.json та fast.log"),
            ]
            for ri, row_vals in enumerate(updates, start=1):
                if ri < len(tbl.rows):
                    for ci, val in enumerate(row_vals):
                        set_cell_text(tbl.rows[ri].cells[ci], val, size=9)

    try:
        doc.save(str(DOC))
        print(f"SAVED {DOC}")
    except PermissionError:
        alt = DOC.with_name(DOC.stem + "_polished.docx")
        doc.save(str(alt))
        print(f"LOCKED; saved {alt}")


if __name__ == "__main__":
    main()
