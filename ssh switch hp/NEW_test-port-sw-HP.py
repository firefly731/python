#!/usr/bin/python
# -*- coding: utf-8 -*-
from netmiko import ConnectHandler
import re
import getpass

hostname = input("Enter an IP address : ")
while re.search(r'^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$', hostname) is None:
    hostname = input("Please enter a valid IP address : ")

INVALID = True
while INVALID == True:
    NB_Switch_OU_Port = input("Enter the number of switch to check or a specific port (ex : 22XX)  : ")
    if re.search(r'^22[0-9]{2}$', NB_Switch_OU_Port) is not None: #check if port is like 22XX then check one switch
        port = int(NB_Switch_OU_Port)
        NB_Switch = 1
        INVALID = False
    elif re.search(r'^[1-9][0-9]?$', NB_Switch_OU_Port) is not None: #if input is between 1 and 99 then check on multiple switch
        port = 2201
        NB_Switch = int(NB_Switch_OU_Port)
        INVALID = False
    else:
        print("Please enter a valid input")

username = input("Login: ")
password = getpass.getpass(prompt='Password: ')


for n in range(NB_Switch):

    hp_procurve = {
        'device_type': 'hp_procurve',
        'ip':   hostname,
        'username': username,
        'password': password,
        'port': port,
        'verbose': True,
    }
    
    try:
        print("")
        net_connect = ConnectHandler(**hp_procurve)

        prompt = net_connect.find_prompt()
        print("")
        print(prompt[:-1])
        print("")
        print("-------------------- Status --------------------")

        MAC = net_connect.send_command("show mac-address")
        MAC_sort = re.findall(r'([^-\s]{6}-[^-\s]{6}.*)\n', MAC)
        #MAC Address   Port  VLAN (pour info, ligne supprimée par la regex)
        #0021f7-b04590 1     3001
        #204c03-14f23c 24    3001
        #204c03-14f23d 24    3001
        status = "fail"
        if MAC_sort != []: status = "success"
        print("show mac-address : {0}".format(status))
    

        INT = net_connect.send_command("show interfaces")
        INT_sort = re.findall(r'(\d.*)\n', INT)
        #Port       Total Bytes    Total Frames   Errors Rx    Drops Tx     Ctrl (pour info, ligne supprimée par la regex)
        #1          0              0              0            0            off
        #2          0              0              0            0            off
        status = "fail"
        if INT_sort != []: 
            status = "success"
            NB_port = len(INT_sort)
        print("show interfaces : {0}".format(status))

        """
        test = INT_sort[0].split(" ")
        test = [i for i in test if i != ""]
        print(test) #['1', '0', '0', '0', '0', 'off']
        """
        
        INT_brief = net_connect.send_command("show interfaces brief")
        INT_brief_sort = re.findall(r'(\d.*)\n', INT_brief)
        #Port  Type       | Alert     Enabled Status Mode       Mode Ctrl (pour info, ligne supprimée par la regex)
        #1     10/100TX   | No        Yes     Down   10FDx      MDIX off
        #2     10/100TX   | No        Yes     Down   10FDx      MDI  off
        status = "fail"
        if INT_brief_sort != []: status = "success"
        print("show interfaces brief : {0}".format(status))


        POE = net_connect.send_command("show power-over-ethernet brief")
        POE_sort = re.findall(r'(\d.*)\n', POE)
        POE_sort = POE_sort[1:]
        #PoE   Pwr  Pwr      Pre-std Alloc Alloc  PSE Pwr PD Pwr  PoE Port    PLC PLC 
        #Port  Enab Priority Detect  Cfg   Actual Rsrvd   Draw    Status      Cls Type (pour info, ligne supprimée par la regex)
        #1     Yes  low      off     usage usage  0.0 W   0.0 W   Searching
        #2     Yes  low      off     usage usage  0.0 W   0.0 W   Searching
        status = "fail"
        if POE_sort != []:
            status = "success"
            NB_port_poe = len(POE_sort)
        print("show power-over-ethernet brief : {0}".format(status))
        print("")


        """
        net_connect.config_mode()
        config_commands = ['vlan 80', 'tagged all', 'exit'] 
        output = net_connect.send_config_set(config_commands)
        print(output)
        net_connect.exit_config_mode()
        """
        net_connect.disconnect()

        print("----------------- Error report -----------------")

        for nb in range(NB_port):

            INT_sort[nb] = INT_sort[nb].split(" ")
            INT_sort[nb] = [i for i in INT_sort[nb] if i != ""]
            
            if "Down" in INT_brief_sort[nb] and INT_sort[nb][1] != "0":
                print("LINK DOWN but traffic was detected on port {0}".format(nb+1))

            MAC_present = False
            for element in MAC_sort:
                element = element.split(" ")
                element = [i for i in element if i != ""]
                if str(nb + 1) in element[1]:
                    MAC_present = True
                    break

            if "Up" in INT_brief_sort[nb] and MAC_present == False:
                print("LINK UP but no mac address on port {0}".format(nb+1))

            if INT_sort[nb][4] != "0":
                print("{0} DROP detected on port {1}".format(INT_sort[nb][4], nb+1))

            if INT_sort[nb][3] != "0":
                print("{0} ERROR detected on port {1}".format(INT_sort[nb][3], nb+1))

            if POE_sort != [] and nb+1 <= NB_port_poe: #check if switch is POE and avoid link port
                POE_sort[nb] = POE_sort[nb].split(" ")
                POE_sort[nb] = [i for i in POE_sort[nb] if i != ""]

                if "Delivering" in POE_sort[nb]:
                    if "Down" in INT_brief_sort[nb]:
                        print("POE detected but no LINK on port {0}".format(nb+1))
                    if MAC_present == False:
                        print("POE detected but no MAC address on port {0}".format(nb+1))

    except OSError as e:
        print(str(e))
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(str(e))
    except paramiko.ssh_exception.AuthenticationException as e:
        print(str(e))
    except paramiko.ssh_exception.socket.timeout as e:
        print(str(e))
    except paramiko.ssh_exception.SSHException as e:
        print(str(e))
    except Exception as e:
        print(e)

    port += 1

input("Enter enter to quit ....")
