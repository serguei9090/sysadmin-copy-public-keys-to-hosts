#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import product

# Load the paths to SSH public key files into a list
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
    print("Incorrect IP range format. Please try again.")

# Build a list of complete IP addresses
ip_addresses = [f"{start_ip.rsplit('.', 1)[0]}.{i}" for i in range(int(start_ip.split(".")[-1]), int(end_ip.split(".")[-1]) + 1)]
print (ip_addresses)
# Load users and passwords
users_file = "users"
with open(users_file) as f:
    users = [tuple(line.strip().split(":")) for line in f]

# Iterate over each IP and copy each SSH public key for each user
failed_auth_count = {}
total_attempts = 0
successful_attempts = 0
for ip_address, (user, password) in product(ip_addresses, users):
    # Check if the host has a connection
    result_ping = subprocess.run(['ping', '-c', '1', '-W', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result_ping.returncode != 0:
        print(f"Could not connect to host {ip_address}")
        continue
        
    # Copy each SSH public key for each user
    for ssh_pub_key in ssh_pub_keys:
        total_attempts += 1
        result = subprocess.run(["sshpass", "-p", password, "ssh-copy-id", "-f", "-i", ssh_pub_key, "-o", "StrictHostKeyChecking=no", f"{user}@{ip_address}"], capture_output=True)
        if result.returncode == 0:
            successful_attempts += 1
            print(f"Key {ssh_pub_key} was successfully copied to {ip_address} for user {user}")
        else:
            failed_auth_count[(user, ip_address)] = failed_auth_count.get((user, ip_address), 0) + 1

# Create a report of failed attempts
if failed_auth_count:
    with open("failed_auth.txt", "w") as f:
        f.write("The following users could not authenticate:\n")
        for (user, ip_address), count in failed_auth_count.items():
            f.write(f"{user} on {ip_address}: {count} failed attempts\n")

# Show a summary message
print(f"Finished. {total_attempts} authentication attempts were made on {len(ip_addresses)*len(users)} combinations of user and IP address on {len(ip_addresses)} IP" )
print(f"{successful_attempts} successful authentications were made in {len(ip_addresses)*len(users)} attempts.")