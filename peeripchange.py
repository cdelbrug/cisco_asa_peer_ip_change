# Peer IP change Script

# 1. Receive input from user via arguments
#     - Old IP
#     - New IP
from sys import argv
import re
from netmiko import ConnectHandler
from ciscoconfparse import CiscoConfParse

script, old_ip, new_ip = argv

print("""
    Peer IP Change Script 0.1
       by Caleb Delbrugge\n""")

asa_ip = input("What's the ASA's IP? ")

# regex to verify that the IP does NOT fall within the RFC 1918 ranges
valid_public_ip = r"(\d+)(?<!10)\.(\d+)(?<!192\.168)(?<!172\.(1[6-9]|2\d|3[0-1]))\.(\d+)\.(\d+)"

cisco_asa = {
    'device_type': 'cisco_asa',
    'ip':    asa_ip,
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco',
}

if re.search(valid_public_ip, old_ip and new_ip):
    pass
else:
    print("The old or new IP specified is either private or invalid, try again")
    raise SystemExit

#2. Search ASA and collect:
#      - confirm if names are configured/enabled
#      - crypto map for peer [exact match]
#      - tunnel-group configuration

net_connect = ConnectHandler(**cisco_asa)

# allow full output from commands instead of having to hit spacebar.
net_connect.send_command('terminal pager 0')

if_names = net_connect.send_command('show run | i names')
names = False

if re.search(r"\bnames\b", if_names):
    print("Names is configured.")
    names = True
    # run show command to find name next to old peer ip and store it in variable
else:
    print("Names is NOT configured.")

crypto_peer_ip = net_connect.send_command('show run map | i {new_ip}')

print(f'''
The crypto map peer line is:\n
{crypto_peer_ip}
''')

exact_match = parse.find_line('{new_ip}')

print(exact_match)

#3. Prompt for confirmation to make changes with proposed changes

#4. Log into the ASA and make the changes

#5. Print configuration and verification commands in terminal
