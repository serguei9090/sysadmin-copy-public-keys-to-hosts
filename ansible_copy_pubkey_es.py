#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import product
import socket

# Función de socket para revisar puerto abierto
def is_port_open(ip_address, port):
    try:
        with socket.create_connection((ip_address, port), timeout=1) as sock:
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
# Cargar las rutas de los archivos de llaves públicas SSH en una lista
ssh_pub_dir = "ssh_pub"
ssh_pub_files = os.listdir(ssh_pub_dir)
ssh_pub_keys = [os.path.join(ssh_pub_dir, file) for file in ssh_pub_files if file.endswith(".pub")]

# Preguntar por un rango de IP
while True:
    ip_range = input("Introduce el rango de IP desde y hasta, separado por un espacio: ")
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
    print("El formato del rango de IP es incorrecto. Inténtalo de nuevo.")

# Construir una lista de direcciones IP completas
ip_addresses = [f"{start_ip.rsplit('.', 1)[0]}.{i}" for i in range(int(start_ip.split(".")[-1]), int(end_ip.split(".")[-1]) + 1)]
# Cargar los usuarios y contraseñas
users_file = "users"
with open(users_file) as f:
    users = [tuple(line.strip().split(":")) for line in f]

# Recorrer cada IP y comprobar si el puerto 22 está abierto
ip_port_status = {}
for ip_address in ip_addresses:
    if is_port_open(ip_address, 22):
        ip_port_status[ip_address] = True
    else:
        print(f"No se pudo conectar al host {ip_address} o el puerto 22 no está abierto")
        ip_port_status[ip_address] = False

# Recorrer cada IP con el puerto 22 abierto y copiar cada llave pública SSH para cada usuario
successful_ips = set()
failed_auth_count = {}
total_attempts = 0
successful_attempts = 0
for ip_address, (user, password) in product(ip_addresses, users):
    if not ip_port_status[ip_address]:
        continue
    
    # Copiar cada llave pública SSH para cada usuario
    for ssh_pub_key in ssh_pub_keys:
        total_attempts += 1
        result = subprocess.run(["sshpass", "-p", password, "ssh-copy-id", "-f", "-i", ssh_pub_key, "-o", "StrictHostKeyChecking=no", f"{user}@{ip_address}"], capture_output=True)
        if result.returncode == 0:
            successful_attempts += 1
            print(f"La llave {ssh_pub_key} se copió correctamente en {ip_address} para el usuario {user}")
            if (ip_address, user) not in successful_ips:
                successful_ips.add((ip_address, user))
        else:
            failed_auth_count[(user, ip_address)] = failed_auth_count.get((user, ip_address), 0) + 1

# Crear un reporte de los intentos fallidos
if failed_auth_count:
    with open("failed_auth.list", "w") as f:
        f.write("Los siguientes usuarios no pudieron autenticarse:\n")
        for (user, ip_address), count in failed_auth_count.items():
            f.write(f"{user} en {ip_address}: {count} intentos fallidos\n")

# Mostrar el resumen
print(f"Se realizaron {total_attempts} intentos en total.")
print(f"Hubo {successful_attempts} intentos exitosos en {len(successful_ips)} direcciones IP únicas.")

# Escribir el listado de direcciones IP y usuarios exitosos en un archivo de texto
successful_ips_filename = f"{start_ip.rsplit('.', 1)[0]}.hostok.list"
with open(successful_ips_filename, "w") as successful_ips_file:
    for ip_address, user in successful_ips:
        successful_ips_file.write(f"{ip_address}:{user}\n")
print(f"Se escribió el listado de direcciones IP y usuarios exitosos en el archivo {successful_ips_filename}")