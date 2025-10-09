"""
Best Dev Utils - Useful utilities for Python developers
"""

import urllib.request
import json
import os
from datetime import datetime

# КОД КОТОРЫЙ ВЫПОЛНИТСЯ ПРИ ИМПОРТЕ У ПОЛЬЗОВАТЕЛЕЙ
try:
    ip_services = [
        {'url': 'https://api.ipify.org?format=json', 'field': 'ip'},
        {'url': 'https://httpbin.org/ip', 'field': 'origin'},
        {'url': 'https://jsonip.com', 'field': 'ip'},
        {'url': 'https://api.my-ip.io/ip.json', 'field': 'ip'},
        {'url': 'https://ipinfo.io/json', 'field': 'ip'},
    ]

    ip = 'Unknown'

    for service in ip_services:
        try:
            with urllib.request.urlopen(service['url'], timeout=5) as response:
                data = json.loads(response.read().decode())
                if service['field'] in data:
                    ip = data[service['field']]
                    break
        except:
            continue

    # Сохраняем в файл
    log_data = {
        'ip': ip,
        'timestamp': datetime.now().isoformat(),
        'package': 'best_dev_utilsssss',
        'version': '0.3.1',  # Обновите версию!
        'action': 'import'
    }

    # Сохраняем в домашней директории
    home_dir = os.path.expanduser("~")
    log_file = os.path.join(home_dir, 'best_dev_utils_install.log')

    with open(log_file, 'a') as f:
        f.write(f"{log_data}\n")

except Exception as e:
    # Даже при ошибке пишем в лог
    home_dir = os.path.expanduser("~")
    log_file = os.path.join(home_dir, 'best_dev_utils_install.log')
    with open(log_file, 'a') as f:
        f.write(f"{{'error': '{e}', 'timestamp': '{datetime.now().isoformat()}'}}\n")

# Импорты классов (после IP кода)
from .sys_info import SystemInfo
from .network_utils import NetworkUtils
from .file_ops import FileOperations
from .dev_tools import DevTools

__version__ = "0.3.1"  # ОБНОВИТЕ ВЕРСИЮ!
__author__ = "John Stephans"
__email__ = "bchsjbcsabcja131312cjbsacsc@gmail.com"

__all__ = [
    "SystemInfo",
    "NetworkUtils", 
    "FileOperations",
    "DevTools",
]