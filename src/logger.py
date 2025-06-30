import logging
import os
import getpass
import re
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'Logs.json')

USERNAME = getpass.getuser()
USER_HOME = os.path.expanduser('~')

# Redact sensitive info (usernames, home paths)
def redact(text):
    if not isinstance(text, str):
        return text
    text = re.sub(re.escape(USER_HOME), '<USER_HOME>', text)
    text = re.sub(re.escape(USERNAME), '<USERNAME>', text)
    return text

def log_json(level, message):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': redact(message)
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

# Logger interface for app code
def log_error(message):
    log_json('ERROR', message)

def log_user(message):
    log_json('INFO', message)

# For compatibility with previous usage
def get_error_logger():
    class DummyLogger:
        def error(self, msg, *args):
            log_error(msg % args if args else msg)
    return DummyLogger()

def get_user_logger():
    class DummyLogger:
        def info(self, msg, *args):
            log_user(msg % args if args else msg)
    return DummyLogger()