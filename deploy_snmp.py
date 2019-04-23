#!/usr/bin/env python3
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException
import getpass, time
# This script connects to the devices and pushes out the specified SNMPv3 configuration. 
# The commands to be configured are in the "commands" variable. 
# "device_list" file must exist, with one IP/hostname per line. 

username = input('Enter your username: ')
password = getpass.getpass(prompt='Enter your password: ', stream=None)
enable_secret = getpass.getpass(prompt='Enter your enable password (press Enter if not required): ', stream=None)
enable_level = '14'

def connect_to(username, password, device, enable_secret): # establish connection to the device
	ios_device = {
		'device_type': 'cisco_ios',
		'ip': device,
		'username': username,
		'password': password,
		'secret': enable_secret
		}
	try:
		net_connect = ConnectHandler(**ios_device)
		return net_connect
	except (AuthenticationException):
		print('Authentication failure while trying: {}'.format(device))
		return None
	except (EOFError):
		print('End of file error while trying {}'.format(device))
		return None
	except (NetMikoTimeoutException):
		print('Timeout while trying {}'.format(device))
		return None
	except Exception as unknown_error:
		print('Unknown error has occured: {}'.format(unknown_error))
		return None

with open('devices_list') as file:				#file containing list of hostname/IPs of devices to be configured.
	devices_list = file.read().splitlines()

# below is the SNMPv3 configuration we are deploying.
commands = ['snmp-server group SecSNMP v3 priv',
'snmp-server user Librenms SecSNMP v3 auth sha authpassword priv aes 128 privpassword',
'snmp-server host 10.2.2.2 trap version 3 priv Librenms']

start_time = time.time() # keeps track of how long it takes the script to finish.

for device in devices_list:	
	print('Connecting to {}'.format(device))
	net_connect = connect_to(username,password,device,enable_secret) # request connection
	if net_connect == None: # if connection is not established, continue on to next device
		print('Could not establish connection, continuing to next device...')
		continue
	if enable_secret != '':
		net_connect.enable(cmd='enable {}'.format(enable_level)) # only needed if enable password is needed.

	print('Configuring {}'.format(device))
	output = net_connect.send_config_set(commands)
	print(output)

total_runtime = time.time() - start_time
print('Total runtime {}'.format(total_runtime))