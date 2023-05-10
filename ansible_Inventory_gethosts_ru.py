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
    
# Запрос на диапазон IP
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
    print("Неверный формат диапазона IP. Попробуйте еще раз.")
    
# Создание списка полных IP-адресов
ip_addresses = [f"{start_ip.rsplit('.', 1)[0]}.{i}" for i in range(int(start_ip.split(".")[-1]), int(end_ip.split(".")[-1]) + 1)]

# Проверка каждого IP-адреса на наличие открытого порта 22 и запись в текстовый файл, если он открыт
имя_файла_списка_хостов = f"{start_ip.rsplit('.', 1)[0]}.host.list"
with open(имя_файла_списка_хостов, "w") as файл_списка_хостов:
    for ip_address in ip_addresses:
        if is_port_open(ip_address, 22):
            файл_списка_хостов.write(ip_address + "\n")
            print(f"Порт 22 открыт на хосте {ip_address}. Добавлен в {имя_файла_списка_хостов}")
        else:
            print(f"Не удалось подключиться к хосту {ip_address} или порт 22 закрыт")

print(f"Запись списка хостов с открытым портом 22 в {имя_файла_списка_хостов} завершена")