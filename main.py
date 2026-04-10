import imaplib
import email
from email.header import decode_header
import time
import ssl
import subprocess
import re
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("UNAME")
password = os.getenv("UPASS")
imap_server = os.getenv("IMAP_SERVER")

# тест бранча

# Папки, которые НЕ нужно проверять (исключения)
EXCLUDE_FOLDERS = {
    'INBOX.Trash',
    'INBOX.Drafts', 
    'INBOX.Sent',
    'INBOX.SPAM',
    'INBOX.Outbox'
}

def decode_utf7(name):
    """Декодирует modified UTF-7 в UTF-8"""
    try:
        return name.encode('utf-8').decode('imap4-utf-7')
    except:
        return name

def get_folder_name(folder_path):
    """Извлекает короткое имя папки из полного пути"""
    parts = folder_path.split('.')
    return decode_utf7(parts[-1]) if parts else folder_path

def send_notification(subject, body="", folder=""):
    """Отправляет уведомление на рабочий стол"""
    try:
        folder_display = get_folder_name(folder) if folder else ""
        folder_info = f"{folder_display}\n" if folder_display else ""
        
        subprocess.run([
            'notify-send',
            '-i', 'mail-unread',
            '-u', 'normal',
            '-t', '5000',
            'Новое письмо',
            f"{folder_info}{body}\n{subject}"
        ], check=True)
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")

def get_all_folders(mail):
    """Получает список всех папок для мониторинга"""
    status, folders = mail.list()
    if status != "OK":
        print(f"Не удалось получить список папок: {status}")
        return []
    
    monitor_folders = []
    
    for f in folders:
        if isinstance(f, bytes):
            f = f.decode('utf-8')
        
        # Извлекаем имя папки из строки списка
        match = re.search(r'"([^"]*)"$', f)
        if not match:
            continue
        
        folder_path = match.group(1)
        
        # Пропускаем исключенные папки
        if folder_path in EXCLUDE_FOLDERS:
            continue
        
        # Пропускаем папки, содержащие SPAM или Trash
        if 'SPAM' in folder_path or 'Trash' in folder_path:
            continue
        
        monitor_folders.append(folder_path)
    
    return monitor_folders

def decode_subject(msg):
    """Безопасно извлекает тему письма"""
    subject = msg.get("Subject")
    
    if subject is None:
        return "(без темы)"
    
    try:
        decoded = decode_header(subject)
        # Берем первую часть заголовка
        if decoded and decoded[0]:
            text, encoding = decoded[0]
            if isinstance(text, bytes):
                # Пытаемся декодировать с разными кодировками
                for enc in [encoding, 'utf-8', 'cp1251', 'koi8-r', 'latin-1']:
                    try:
                        return text.decode(enc or 'utf-8')
                    except:
                        continue
            return str(text)
    except Exception as e:
        print(f"Ошибка декодирования темы: {e}")
    
    return "(ошибка декодирования)"

def check_mail():
    mail = None
    try:
        # Создаем контекст с ослабленной безопасностью
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers('DEFAULT:@SECLEVEL=1')
        
        # Подключаемся
        mail = imaplib.IMAP4_SSL(imap_server, ssl_context=context)
        mail.login(username, password)
        
        # Получаем список всех папок автоматически
        folders = get_all_folders(mail)
        
        if not folders:
            print("Нет папок для проверки")
            return
        
        # Проверяем каждую папку
        for folder_path in folders:
            # Выбираем папку
            status, select_data = mail.select(folder_path)
            if status != "OK":
                print(f"Не удалось выбрать папку '{get_folder_name(folder_path)}': {status}")
                continue
            
            # Ищем непрочитанные письма
            status, messages = mail.search(None, 'UNSEEN')
            
            if messages[0]:
                count = len(messages[0].split())
                folder_name = get_folder_name(folder_path)
                print(f"Найдено {count} непрочитанных в '{folder_name}'")
                
                for num in messages[0].split():
                    # Получаем письмо
                    status, data = mail.fetch(num, '(RFC822)')
                    for response_part in data: 
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Безопасно декодируем тему
                            subject = decode_subject(msg)
                            
                            # Получаем отправителя
                            from_ = email.utils.parseaddr(msg["From"])[1]
                            if not from_:
                                from_ = msg.get("From", "неизвестный")
                            
                            print(f"От: {from_}")
                            print(f"Тема: {subject}")
                            
                            # Отправляем уведомление
                            send_notification(subject, f"От: {from_}", folder_path)

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Закрываем подключение
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass

# Запуск проверки
if __name__ == "__main__":
    print("Мониторинг почты запущен...")
    print("Папки будут определены автоматически\n")
    
    while True:
        check_mail()
        time.sleep(10)
