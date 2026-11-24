# Лабораторна робота 5 — розташування файлів

**Звіт**

- `Ашомка_Андрій_ІМ-34_ЛР5.docx`

**Дамп (не входить до архіву матеріалів 6.2)**

- `lr5_v02.pcap` — варіант 02

**Матеріали пункту 6.2** — `evidence/`

### Команди та скрипти

- `evidence/scripts/count_syn_by_src.py` — підрахунок SYN без ACK за джерелом
- `evidence/scripts/summarize_eve.py` — зведення alerts з eve.json
- `evidence/scripts/investigate.py` — розширення (а): автоматичне розслідування → JSON
- `evidence/scripts/incident.json` — результат investigate.py

### Правила та Suricata

- `evidence/rules/local.rules` — три власні правила (sid 1000001–1000003)
- `evidence/suricata/suricata.yaml` — конфіг з `HOME_NET: [10.42.48.0/24]`
- `evidence/suricata/eve-fragment.json` — фрагмент alerts ET Open
- `evidence/suricata/eve-custom-fragment.json` — alerts власних правил
