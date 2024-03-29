#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import product
import socket

# Функция сокета для проверки открытого порта
def is_port_open(ip_address, port):
    try:
        with socket.create_connection((ip_address, port), timeout=1) as sock:
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
# Загрузить пути к файлам открытых ключей SSH в список
ssh_pub_dir = "ssh_pub"
ssh_pub_files = os.listdir(ssh_pub_dir)
ssh_pub_keys = [os.path.join(ssh_pub_dir, file) for file in ssh_pub_files if file.endswith(".pub")]

# Запросить диапазон IP-адресов
while True:
    ip_range = input("Введите диапазон IP-адресов от и до, разделенных пробелом: ")
    parts = ip_range.split()
    if len(parts) == 2:
        start_ip, end_ip = parts
        start_parts = start_ip.split(".")
        end_parts = end_ip.split(".")
        if len(start_parts) == 4 and len(end_parts) == 4:
            valid_range = True
            for part in start_parts + end_parts:
                if not part.isdigit() or int(part) < 0 or int(part) > 255:
                    valid_range = False
                    break
            if valid_range:
                break
    print("Неправильный формат диапазона IP-адресов. Попробуйте снова.")

# Составить список полных IP-адресов
ip_addresses = [f"{start_ip.rsplit('.', 1)[0]}.{i}" for i in range(int(start_ip.split(".")[-1]), int(end_ip.split(".")[-1]) + 1)]
# Загрузить пользователей и пароли
users_file = "users"
with open(users_file) as f:
    users = [tuple(line.strip().split(":")) for line in f]

# Проверить каждый IP-адрес и проверить, открыт ли порт 22
ip_port_status = {}
for ip_address in ip_addresses:
    if is_port_open(ip_address, 22):
        ip_port_status[ip_address] = True
    else:
        print(f"Не удалось подключиться к хосту {ip_address} или порт 22 закрыт")
        ip_port_status[ip_address] = False

# Скопировать каждый открытый ключ SSH для каждого пользователя на каждом IP-адресе
successful_ips = set()
failed_auth_count = {}
total_attempts = 0
successful_attempts = 0
for ip_address, (user, password) in product(ip_addresses, users):
    if not ip_port_status[ip_address]:
        continue
    
    # Скопировать каждый открытый ключ SSH для каждого пользователя
    for ssh_pub_key in ssh_pub_keys:
        total_attempts += 1
        result = subprocess.run(["sshpass", "-p", password, "ssh-copy-id", "-f", "-i", ssh_pub_key, "-o", "StrictHostKeyChecking=no", f"{user}@{ip_address}"], capture_output=True)
        if result.returncode == 0:
            successful_attempts += 1
            print(f"Ключ {ssh_pub_key} успешно скопирован на {ip_address} для пользователя {user}")
            if (ip_address, user) not in successful_ips:
                successful_ips.add((ip_address, user))
        else:
            failed_auth_count[(user, ip_address)] = failed_auth_count.get((user, ip_address), 0) + 1

# Создать отчет о неудачных попытках
if failed_auth_count:
    with open("failed_auth.list", "w") as f:
        f.write("Следующие пользователи не смогли аутентифицироваться:\n")
        for (user, ip_address), count in failed_auth_count.items():
            f.write(f"{user} на {ip_address}: {count} неудачных попыток\n")

# Показать сводку
print(f"Всего было сделано {total_attempts} попыток.")
print(f"Было {successful_attempts} успешных попыток на {len(successful_ips)} уникальных IP-адресах.")

# Записать список успешных IP-адресов и пользователей в текстовый файл
successful_ips_filename = f"{start_ip.rsplit('.', 1)[0]}.hostok.list"
with open(successful_ips_filename, "w") as successful_ips_file:
    for ip_address, user in successful_ips:
        successful_ips_file.write(f"{ip_address}:{user}\n")
print(f"Список успешных IP-адресов и пользователей был записан в файл {successful_ips_filename}")