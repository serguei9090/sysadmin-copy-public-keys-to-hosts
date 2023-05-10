#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import product
import socket

# Socket function to check open port
def is_port_open(ip_address, port):
    try:
        with socket.create_connection((ip_address, port), timeout=1) as sock:
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
# Ask for an IP range
while True:
    ip_range = input("Enter the IP range from and to, separated by a space: ")
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
    print("The format of the IP range is incorrect. Please try again.")
    
# Build a list of complete IP addresses
ip_addresses = [f"{start_ip.rsplit('.', 1)[0]}.{i}" for i in range(int(start_ip.split(".")[-1]), int(end_ip.split(".")[-1]) + 1)]

# Iterate over each IP and check if port 22 is open, and write the IP to a text file if it is
host_list_filename = f"{start_ip.rsplit('.', 1)[0]}.host.list"
with open(host_list_filename, "w") as host_list_file:
    for ip_address in ip_addresses:
        if is_port_open(ip_address, 22):
            host_list_file.write(ip_address + "\n")
            print(f"Port 22 is open on host {ip_address}. Added to {host_list_filename}")
        else:
            print(f"Could not connect to host {ip_address} or port 22 is not open")

print(f"Finished writing the list of hosts with open port 22 to {host_list_filename}")