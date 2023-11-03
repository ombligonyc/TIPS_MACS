import re
import subprocess
import os
import requests
from keyboard import testKeyboard





def parse_hardware_info(sph, disk):
    info = {}

    sphpatterns = {
        "Model": r"Model Name: (.+)",
        "Identifier": r"Model Identifier: (.+)",
        "Processor": r"Processor Name: (.+)",
        "Processor_Speed": r"Processor Speed: (.+)",
        "Number of Processors": r"Number of Processors: (.+)",
        "Total Number of Cores": r"Total Number of Cores: (.+)",
        "L2 Cache": r"L2 Cache \(per Core\): (.+)",
        "L3 Cache": r"L3 Cache: (.+)",
        "Hyper-Threading Technology": r"Hyper-Threading Technology: (.+)",
        "Memory": r"Memory: (.+)",
        "System Firmware Version": r"System Firmware Version: (.+)",
        "OS Loader Version": r"OS Loader Version: (.+)",
        "Serial_Number": r"Serial Number \(system\): (.+)",
        "Hardware UUID": r"Hardware UUID: (.+)",
        "Provisioning UDID": r"Provisioning UDID: (.+)",
        "Activation_Lock_Status": r"Activation Lock Status: (.+)"
    }
    diskpattern = r"Disk Size:\s+([\d\.]+)\sGB"

    match = re.search(diskpattern, disk)
    if match:
        disk_size = match.group(1)
        info['Storage'] = disk_size
    else:
        print("Disk size not found")

    for line in sph.splitlines():  # Iterate over each line
        for key, pattern in sphpatterns.items():
            match = re.search(pattern, line)
            if match:
                info[key] = match.group(1).strip()


    return info
batteryCondition = subprocess.Popen("system_profiler SPPowerDataType | grep 'Condition' | awk '{print $2}'", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
batteryCycles = subprocess.Popen("system_profiler SPPowerDataType | grep 'Cycle Count' | awk '{print $3}'", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
SPH = subprocess.Popen("system_profiler SPHardwareDataType", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
DISK = subprocess.Popen("diskutil info disk0 | grep 'Disk Size'", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
hardware_info = parse_hardware_info(SPH, DISK)

def postHardware(hardware_info):
    url = 'http://10.1.101.4:1111/main/post_macbook/'
    spec = {
        'po': hardware_info['refnb'],
        'class': 'Laptop',
        'ItemNo': hardware_info['Model'],
        'assetnb':hardware_info['assetnb'],
        'refnb':hardware_info['refnb'],
        'id': hardware_info['Identifier'],
        'quality':hardware_info['quality'],
        'proc': hardware_info['Processor'],
        'ram': hardware_info['Memory'],
        'storage': hardware_info['Storage'],
        'serial': hardware_info['Serial_Number'],
        'color': hardware_info['color'],
        'size': hardware_info['size'],
        'tech_notes': hardware_info['tech_notes'],
        'batteryCondition' :batteryCondition,
        'batteryCycles' : batteryCycles
    }
    print(str(spec))
    # Organizing the data payload for POST request
    data = {
        'po': hardware_info['refnb'],
        'assetnb': hardware_info['assetnb'],
        'serial': hardware_info['Serial_Number'],
        'spec': str(spec)
    }
    response = requests.post(url, data = data)
    print(response.status_code)
    print(response.json())


os.system('clear')

testKeyboard()

hardware_info['assetnb'] = input('Enter Asset Number: ')
while len(hardware_info['assetnb']) < 10:
    hardware_info['assetnb'] = input('Asset Number short. Enter Asset Number: ')
os.system('clear')


hardware_info['refnb'] = input('Enter PO: ')
os.system('clear')

print('P: PASS')
print('F: FAIL')
print('S: FOR PARTS/SCRAP')

hardware_info['quality'] = input('Enter quality: ')

if hardware_info['quality'] == 'P' or hardware_info['quality'] == 'p':
    hardware_info['quality'] = 'PASS'

if hardware_info['quality'] == 'F' or hardware_info['quality'] == 'f':
    hardware_info['quality'] = 'FAIL'

if hardware_info['quality'] == 's' or hardware_info['quality'] == 'S':
    hardware_info['quality'] = 'FOR PARTS / SCRAP)'

while hardware_info['quality'] not in ['P','p','F','f','S','s']:
    print('P: PASS')
    print('F: FAIL')
    print('S: FOR PARTS/SCRAP')

    hardware_info['quality'] = input('Enter quality: ')
os.system('clear')

hardware_info['color'] = input('Enter color: ')
os.system('clear')

hardware_info['size'] = input('Enter Size: ')
while hardware_info['size'] not in ['12','13','15']:
    print('12,13, or 15')
    hardware_info['size'] = input('Enter Size: ')

os.system('clear')

hardware_info['tech_notes'] = input('Additional Notes: ')


postHardware(hardware_info)


