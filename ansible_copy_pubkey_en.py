#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import product
import socket

# Socket function to check for open port
def is_port_open(ip_address, port):
    try:
        with socket.create_connection((ip_address, port), timeout=1) as sock:
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
# Load the paths of SSH public key files into a list
ssh_pub_dir = "ssh_pub"
ssh_pub_files = os.listdir(ssh_pub_dir)
ssh_pub_keys = [os.path.join(ssh_pub_dir, file) for file in ssh_pub_files if file.endswith(".pub")]

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
# Load the users and passwords
users_file = "users"
with open(users_file) as f:
    users = [tuple(line.strip().split(":")) for line in f]

# Iterate over each IP and check if port 22 is open
ip_port_status = {}
for ip_address in ip_addresses:
    if is_port_open(ip_address, 22):
        ip_port_status[ip_address] = True
    else:
        print(f"Could not connect to host {ip_address} or port 22 is not open")
        ip_port_status[ip_address] = False

# Iterate over each IP with port 22 open and copy each SSH public key for each user
successful_ips = set()
failed_auth_count = {}
total_attempts = 0
successful_attempts = 0
for ip_address, (user, password) in product(ip_addresses, users):
    if not ip_port_status[ip_address]:
        continue
    
    # Copy each SSH public key for each user
    for ssh_pub_key in ssh_pub_keys:
        total_attempts += 1
        result = subprocess.run(["sshpass", "-p", password, "ssh-copy-id", "-f", "-i", ssh_pub_key, "-o", "StrictHostKeyChecking=no", f"{user}@{ip_address}"], capture_output=True)
        if result.returncode == 0:
            successful_attempts += 1
            print(f"The key {ssh_pub_key} was successfully copied to {ip_address} for user {user}")
            if (ip_address, user) not in successful_ips:
                successful_ips.add((ip_address, user))
        else:
            failed_auth_count[(user, ip_address)] = failed_auth_count.get((user, ip_address), 0) + 1

# Create a report of failed attempts
if failed_auth_count:
    with open("failed_auth.txt", "w") as f:
        f.write("The following users could not authenticate:\n")
        for (user, ip_address), count in failed_auth_count.items():
            f.write(f"{user} at {ip_address}: {count} failed attempts\n")

# Show the summary
print(f"A total of {total_attempts} attempts were made.")
print(f"There were {successful_attempts} successful attempts on {len(successful_ips)} unique IP addresses.")

# Write the list of successful IP addresses and users to a text file
successful_ips_filename = f"{start_ip.rsplit('.', 1)[0]}.hostok.list"
with open(successful_ips_filename, "w") as successful_ips_file:
    for ip_address, user in successful_ips:
        successful_ips_file.write(f"{ip_address}:{user}\n")
print(f"The list of successful IP addresses and users was written to the file {successful_ips_filename}")