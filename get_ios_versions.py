#!/usr/bin/env python3
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, AuthenticationException
import getpass, re, json
# script collects the IOS version of all the devices and pairs it with its device hostname or IP, in json format
# a collected_versions.txt file is created in present working directory
# devices_list file must exist and contain the hostnames or IP addresses of the devices to be accessed, 1 per line
# if you require an enable password, be sure to set the enable level

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

try:
	with open('devices_list') as file: # open list of devices that we are working with
		devices_list = file.read().splitlines()
except:
	print('Does the file devices_list file exist?\nCheck for issues with the devices_list file.')

collected_results = {} # IOS versions will be written with the IP address/hostname to this dictionary. 

for device in devices_list:
	print('Connecting to {}'.format(device))
	net_connect = connect_to(username,password,device,enable_secret) # request connection
	if net_connect == None: # if connection is not established, continue on to next device
		print('Could not establish connection, continuing to next device...')
		continue
	if enable_secret != '':
		net_connect.enable(cmd='enable {}'.format(enable_level)) # only needed if enable password is needed
	print('Retrieving output...')
	output = net_connect.send_command('show version') # get 'show version' output
	filtered = re.search(r"^Cisco.*Version (\S+),", output).group(1) # filter out version number from complete output
	collected_results[device] = filtered

try:
	print('Writing to file...')
	with open('collected_versions.txt', 'w') as file: # create a file and write the results in JSON format
		file.write(json.dumps(collected_results))
except Exception as unknown_error:
	print(unknown_error)