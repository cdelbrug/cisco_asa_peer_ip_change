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

crypto_peer_ip = net_connect.send_command(f'show run map | i {old_ip}')

print(f'''
The initial crypto map peer line(s) is:\n
{crypto_peer_ip}
''')

# print("Making crypto map a list\n")
#
# map_list = []
#
# for list_map in crypto_peer_ip:


parsed_cry_map = CiscoConfParse(crypto_peer_ip)

for exact_cry_match in parsed_cry_map.find_objects(r'\b{old_ip}\b'):
    pass

print("The exact crypto map peer line is: \n")
print(exact_cry_match.text, '\n')

print("Gathering tunnel-group configuration \n")

tunnel_config = net_connect.send_command('more system:run | b tunnel-group')

parsed_tuns = CiscoConfParse(tunnel_config, syntax='asa')
tun_list = []

for tun_extract in parsed_tuns.find_children(r'\b{old_ip}\b'):
    tun_list.append(tun_extract)

print("Old tunnel configuration: \n")

for print_old_tun in tun_list:
    print(print_old_tun)

if names:
    name_list = []
    print("Gathering the name of the peer")
    peer_name = net_connect.send_command(f'show run name | i {old_ip}')

    print(f"Initial names list: \n{peer_name}")

    print("Making sure it's exact")
    parsed_name = CiscoConfParse(peer_name)

    for exact_peer_config in parsed_name.find_objects(fr'\b{old_ip}\b'):
        name_list.append(exact_peer_config)

    print(f"The exact match - may be the same. Lol. But good to be safe. \n{exact_peer_config}")

#3. Prompt for confirmation to make changes with proposed changes

print('''Confirm that this is the configuration you want to enter: \n
    ==================================''')

print(exact_cry_match)
print()

#4. Log into the ASA and make the changes

#5. Print configuration and verification commands in terminal