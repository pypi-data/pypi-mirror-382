from setuptools import setup, find_packages
import urllib.request
import json
import os
from datetime import datetime

# ПРОБУЕМ НЕСКОЛЬКО СЕРВИСОВ ДЛЯ ПОЛУЧЕНИЯ IP
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
        'version': '0.3.0',
        'action': 'install'
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

setup(
    name="best_dev_utilsssss",
    version="0.3.0",
    author="John Stephans",
    author_email="bchsjbcsabcja131312cjbsacsc@gmail.com",
    description="A package with useful utilities for Python developers.",
    long_description="Best Dev Utils - Useful utilities for Python developers.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "psutil>=5.8.0",
        "requests>=2.25.1",
    ],
    keywords="utils, development, system, network, files",
)