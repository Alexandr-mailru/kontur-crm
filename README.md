# Контур CRM

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)

Демо-CRM на Django для портфолио: клиенты, сделки, задачи, воронка. С учётом ФЗ‑152 и авторских прав.

**Репозиторий:** https://github.com/Alexandr-mailru/kontur-crm

## Возможности

- клиенты с указанием основания обработки ПДн контакта;
- сделки по этапам воронки;
- задачи с дедлайнами;
- дашборд;
- регистрация с согласием на обработку ПДн;
- политика конфиденциальности, авторские права, cookie-баннер.

## Быстрый старт

```bash
git clone https://github.com/Alexandr-mailru/kontur-crm.git
cd kontur-crm
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env_sample .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Демо-вход: **demo** / **demo12345**

## Правовая информация

- `/privacy/` — политика конфиденциальности (ФЗ‑152);
- `/copyright/` — авторские права и лицензии;
- cookie: только `sessionid` и `csrftoken`, без аналитики.

## Автор

Портфолио-проект. GitHub: **Alexandr-mailru**

Другие работы: [лендинги](https://alexandr-mailru.github.io/landings-portfolio/)
