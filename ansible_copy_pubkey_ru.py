#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import product

# Загрузить пути к файлам открытых ключей SSH в список
ssh_pub_dir = "ssh_pub"
ssh_pub_files = os.listdir(ssh_pub_dir)
ssh_pub_keys = [os.path.join(ssh_pub_dir, file) for file in ssh_pub_files if file.endswith(".pub")]

# Запросить диапазон IP
while True:
    ip_range = input("Введите диапазон IP от и до, разделенный пробелом: ")
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
    print("Неправильный формат диапазона IP. Попробуйте еще раз.")

# Создать список полных адресов IP
ip_addresses = [f"{start_ip.rsplit('.', 1)[0]}.{i}" for i in range(int(start_ip.split(".")[-1]), int(end_ip.split(".")[-1]) + 1)]

# Загрузить пользователей и пароли
users_file = "users"
with open(users_file) as f:
    users = [tuple(line.strip().split(":")) for line in f]

# Перебрать каждый IP и скопировать каждый открытый ключ SSH для каждого пользователя
failed_auth_count = {}
total_attempts = 0
successful_attempts = 0
for ip_address, (user, password) in product(ip_addresses, users):
    # Проверить, есть ли подключение к хосту
    result_ping = subprocess.run(['ping', '-c', '1', '-W', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result_ping.returncode != 0:
        print(f"Не удалось подключиться к хосту {ip_address}")
        continue
        
    # Скопировать каждый открытый ключ SSH для каждого пользователя
    for ssh_pub_key in ssh_pub_keys:
        total_attempts += 1
        result = subprocess.run(["sshpass", "-p", password, "ssh-copy-id", "-f", "-i", ssh_pub_key, "-o", "StrictHostKeyChecking=no", f"{user}@{ip_address}"], capture_output=True)
        if result.returncode == 0:
            successful_attempts += 1
            print(f"Ключ {ssh_pub_key} успешно скопирован на {ip_address} для пользователя {user}")
        else:
            failed_auth_count[(user, ip_address)] = failed_auth_count.get((user, ip_address), 0) + 1

# Создать отчет о неудачных попытках аутентификации
if failed_auth_count:
    with open("failed_auth.txt", "w") as f:
        f.write("Следующие пользователи не смогли аутентифицироваться:\n")
        for (user, ip_address), count in failed_auth_count.items():
            f.write(f"{user} на {ip_address}: {count} неудачных попыток\n")

# Показать сообщение об итогах
print(f"Завершено. Было выполнено {total_attempts} попыток аутентификации в {len(ip_addresses)*len(users)} комбинаций пользователя и IP-адреса на {len(ip_addresses)} IP-адресов")
print(f"Было успешно выполнено {successful_attempts} попыток аутентификации из {len(ip_addresses)*len(users)} попыток.")