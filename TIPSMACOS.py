import pygame
import sys
import re
import subprocess
import os
import requests




def testKeyboard():
    pygame.init()


    #screen = pygame.display.set_mode((width, height))
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    pygame.display.set_caption('Keyboard Test')

    keys_to_test = set([
        pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i,
        pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
        pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z, pygame.K_0,
        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
        pygame.K_SPACE, pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_TAB, pygame.K_LSHIFT, pygame.K_BACKSLASH, pygame.K_EQUALS,pygame.K_MINUS,
        pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_LALT, pygame.K_BACKQUOTE, pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET, pygame.K_CAPSLOCK,
        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 
        # Add other keys as needed
    ])

    pressed_keys = set()

    font = pygame.font.Font(None, 36)

    def render_text():
        screen.fill((255, 255, 255))
        message = "Pressed keys: {}/{}".format(len(pressed_keys), len(keys_to_test))
        text = font.render(message, True, (0, 0, 0))
        screen.blit(text, (20, 20))
        pygame.display.flip()

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in keys_to_test:
                    pressed_keys.add(event.key)
                render_text()

            if pressed_keys == keys_to_test:
                
                pygame.quit()
                return('p')
                #sys.exit()










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

def getHWInfo():
    SPH = subprocess.Popen("system_profiler SPHardwareDataType", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    DISK = subprocess.Popen("diskutil info disk0 | grep 'Disk Size'", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    hardware_info = parse_hardware_info(SPH, DISK)
    return hardware_info


def getBatteryState():
    batteryCondition = subprocess.Popen("system_profiler SPPowerDataType | grep 'Condition' | awk '{print $2}'", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    batteryCycles = subprocess.Popen("system_profiler SPPowerDataType | grep 'Cycle Count' | awk '{print $3}'", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return batteryCondition, batteryCycles

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
        'batteryCondition' :hardware_info['batteryCondition'],
        'batteryCycles' : hardware_info['batteryCycles'],
        'wiped' : hardware_info['wiped'],
        'tech_initals' : hardware_info['initals']
    }
    print(str(spec))
    data = {
        'po': hardware_info['refnb'],
        'assetnb': hardware_info['assetnb'],
        'serial': hardware_info['Serial_Number'],
        'spec': str(spec)
    }
    response = requests.post(url, data = data)
    print(response.status_code)
    print(response.json())


def draw_text_input(screen, message, font, input_rect, color_active, color_passive, color, active,additionalPrompt=None):
    if active:
        color = color_active
    else:
        color = color_passive
    if additionalPrompt:
        if len(additionalPrompt) > 50:
            part_length = len(additionalPrompt) // 8
            parts = [additionalPrompt[i:i+part_length] for i in range(0, len(additionalPrompt), part_length)]

            if len(parts) > 8:
                parts[5] = ''.join(parts[7:])
                parts = parts[:8]

            texts = [font.render(part, True, (0, 0, 0)) for part in parts]

            for i, text in enumerate(texts):
                screen.blit(text, (20, 40 + i*25)) 
        else:
            text = font.render(additionalPrompt, True, (0, 0, 0))
            screen.blit(text, (20, 40))

    text_surface = font.render(message, True, (0, 0, 0))
    screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
    pygame.display.flip()

def get_text_input(screen, prompt,  font, input_box, color_active, color_passive, max_length=None, additionalPrompt=None,):
    input_active = True
    user_input = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = not input_active
                else:
                    input_active = True
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        if max_length is None or len(user_input) >= max_length:
                            return user_input
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        if max_length is None or len(user_input) < max_length:
                            user_input += event.unicode

        screen.fill((255, 255, 255)) 
        draw_text_input(screen, prompt + user_input, font, input_box, color_active, color_passive, (0, 0, 0), input_active, additionalPrompt)
        pygame.display.flip()

def main():

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Hardware Info Input')
    font = pygame.font.Font(None, 32)

    input_box_asset = pygame.Rect(100, 100, 140, 32)
    input_box_po = pygame.Rect(100, 150, 140, 32)
    input_box_color = pygame.Rect(100, 200, 140, 32)
    input_box_size = pygame.Rect(100, 250, 140, 32)
    input_box_tech_notes = pygame.Rect(100, 300, 140, 32)

    color_active = pygame.Color('lightskyblue3')
    color_passive = pygame.Color('gray15')
    color = color_passive

    hardware_info = getHWInfo()
    batteryCondition, batteryCycles = getBatteryState()
    hardware_info['batteryCondition'] = batteryCondition
    hardware_info['batteryCycles'] = batteryCycles
    hardware_info['tech_initals'] = get_text_input(screen, 'Enter Passcode: ', font, input_box_asset, color_active, color_passive, 4)
    hardware_info['keyboard'] = testKeyboard()

    # User input
    hardware_info['assetnb'] = get_text_input(screen, 'Enter Asset Number: ', font, input_box_asset, color_active, color_passive, 10)
    hardware_info['refnb'] = get_text_input(screen, 'Enter PO: ', font, input_box_po, color_active, color_passive)




    hardware_info['quality'] = get_text_input(screen,'Enter Quality: ', font, input_box_po, color_active, color_passive, additionalPrompt='P: PASS, F: FAIL')
    while hardware_info['quality'] not in ['P','p','F','f']:
        hardware_info['quality'] = get_text_input(screen,'Enter Quality: ', font, input_box_po, color_active, color_passive, additionalPrompt='P: PASS, F: FAIL')

    hardware_info['color'] = get_text_input(screen,'Enter Color: ', font, input_box_po, color_active, color_passive, additionalPrompt='space grey, silver, grey, sg, g, s') 
    while hardware_info['color'] not in ['grey','gray','space grey','space gray', 'black','silver','white','g','sg','s']:
        hardware_info['color'] = get_text_input(screen,'Enter Color: ', font, input_box_po, color_active, color_passive)

    hardware_info['size'] = get_text_input(screen,'Enter Size: ', font, input_box_po, color_active, color_passive)

    hardware_info['wiped'] = get_text_input(screen,'Has this device been sanitized? ', font, input_box_po, color_active, color_passive, additionalPrompt='y, n')
    while hardware_info['wiped'] not in ['y','n']:
        hardware_info['wiped'] = get_text_input(screen,'Has this device been sanitized? ', font, input_box_po, color_active, color_passive, additionalPrompt='y, n')

    hardware_info['tech_notes'] = get_text_input(screen,'Additional Notes: ', font, input_box_po, color_active, color_passive)

    confirmation = get_text_input(screen,' ', font, input_box_po, color_active, color_passive, additionalPrompt=str(hardware_info))

#    hardware_info['assetnb'] = input('Enter Asset Number: ')
#    while len(hardware_info['assetnb']) < 10:
#        hardware_info['assetnb'] = input('Asset Number short. Enter Asset Number: ')
 #   os.system('clear')





#    while hardware_info['quality'] not in ['P','p','F','f','S','s']:
#        print('P: PASS')
#        print('F: FAIL')
#        print('S: FOR PARTS/SCRAP')

#        hardware_info['quality'] = input('Enter quality: ')
#    os.system('clear')

#    hardware_info['color'] = input('Enter color: ')
#    os.system('clear')

    #hardware_info['size'] = input('Enter Size: ')
   # while hardware_info['size'] not in ['12','13','15']:
  #      print('12,13, or 15')
 #       hardware_info['size'] = input('Enter Size: ')

#    os.system('clear')

    #hardware_info['tech_notes'] = input('Additional Notes: ')




    postHardware(hardware_info)

if __name__ == "__main__":
    main()
