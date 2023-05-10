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

# Recorrer cada IP y comprobar si el puerto 22 está abierto, y escribir la IP en un archivo de texto si lo está
nombre_archivo_lista_hosts = f"{start_ip.rsplit('.', 1)[0]}.host.list"
with open(nombre_archivo_lista_hosts, "w") as archivo_lista_hosts:
    for ip_address in ip_addresses:
        if is_port_open(ip_address, 22):
            archivo_lista_hosts.write(ip_address + "\n")
            print(f"El puerto 22 está abierto en el host {ip_address}. Agregado a {nombre_archivo_lista_hosts}")
        else:
            print(f"No se pudo conectar al host {ip_address} o el puerto 22 no está abierto")

print(f"Se terminó de escribir la lista de hosts con el puerto 22 abierto en {nombre_archivo_lista_hosts}")