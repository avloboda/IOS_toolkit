#!/usr/bin/env python3
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, AuthenticationException
import getpass, time
# script pulls running configuration on device, and writes it to file. "configs" directory must exist in working directory.
# devices_list file must exist and contain the hostnames or IP addresses of the devices to be accessed, 1 per line
# if you require an enable password, be sure to set the enable level

username = input('Enter your username: ')
password = getpass.getpass(prompt='Enter your password: ', stream=None)
enable_secret = getpass.getpass(prompt='Enter your enable password (press Enter if not required): ', stream=None)
enable_level = '14'

current_date = time.strftime('%m-%d-%Y') # get todays date; will be appended to config filenames.

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

start_time = time.time() # time the script

try:
	with open('devices_list') as file: # open list of devices that we are working with
		devices_list = file.read().splitlines()
except:
	print('Does the file devices_list file exist?\nCheck for issues with the devices_list file.')

for device in devices_list:
	print('Connecting to {}'.format(device))
	net_connect = connect_to(username,password,device,enable_secret) # request connection
	if net_connect == None: # if connection is not established, continue on to next device
		print('Could not establish connection, continuing to next device...')
		continue
	if enable_secret != '':
		net_connect.enable(cmd='enable {}'.format(enable_level)) # only needed if enable password is needed.
	print('Retrieving output...')
	output = net_connect.send_command('show running') # get output

	try:
		print('Writing to file...')
		with open('configs/{}-{}.txt'.format(device, current_date), 'a') as file: # create a file and write the results
			file.write(output)
	except Exception as unknown_error:
		print(unknown_error)

total_runtime = time.time() - start_time # get runtime 
print('Total runtime {}'.format(total_runtime))