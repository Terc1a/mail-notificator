# 📬 Mail Notifier

**Mail Notifier** — лёгкий daemon для Linux, который отправляет pop-up уведомления о новых письмах прямо на рабочий стол.

---

## 🚀 Возможности

- 📥 Проверка почты по IMAP  
- 🔔 Desktop-уведомления о новых письмах  
- ⚙️ Работа в фоне (daemon)  
- 🐍 Минималистичный стек: `python3 + imaplib`  
- 🧩 Простая настройка через `.env`  

---

## 🛠️ Технологии

- Python 3  
- `imaplib` (стандартная библиотека)

---

## 📦 Установка

```bash
git clone https://github.com/Terc1a/mail-notificator.git
cd mail-notificator

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## ⚙️ Настройка

- Создайте файл .env в корне проекта и заполните его:
```env
IMAP_SERVER=your_imap_server
EMAIL=your_email
PASSWORD=your_password
```

## ▶️ Запуск

```bash
python3 main.py
```

## 🔄 Запуск как сервис (systemd)

- В проекте уже есть готовый unit-файл. Для установки:
```bash
sudo cp mail-notifier.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl enable mail-notifier
sudo systemctl start mail-notifier
```

- Проверка статуса:
```bash
systemctl status mail-notifier
```

## 🧠 Как это работает
- Подключение к почтовому серверу через IMAP
- Периодическая проверка новых писем
- Отправка системного уведомления при обнаружении нового письма

## 📌 Примечания
- Только для Linux (используются системные уведомления)
- Можно запускать вручную или через systemd
