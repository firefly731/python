#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko #library for ssh connection
import re
import getpass
import time

def recieveData(sleep=1): #change sleep value if needed
    tCheck = 0
    while not conn.recv_ready():
        time.sleep(sleep)
        tCheck+=1
        if tCheck >=10:
            print("time out")

hostname = input("Enter an IP address : ")
while re.search(r'^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$', hostname) is None:
    hostname = input("Please enter a valid IP address : ")

username = input("Login: ")

password = getpass.getpass(prompt='Password: ')

nb = False
while nb == False:
    NB_Switch = input("Enter the number of switch : ")
    try:
        NB_Switch = int(NB_Switch)
    except ValueError:
        print("Please enter a number")
    else:
        nb = True

other_vlan = 1
while other_vlan == 1:
    nb = False
    while nb == False:
        vlan = input("Enter VLAN number : ")
        try:
            vlan = int(vlan)
        except ValueError:
            print("Please enter a number")
        else:
            nb = True

    if vlan == 2020:
        name_vlan = "IPTV"
        nb = False
        while nb == False:
            switch_server = input("Enter SWITCH number where IPTV server is connected : ")
            try:
                switch_server = int(switch_server)
            except ValueError:
                print("Please enter a number")
            else:
                nb = True
        port_untagged = input("Enter port to untagged otherwise press Enter (example : 1-3,5,8-10): ")
        if port_untagged != "":
            while re.search(r'^[\d]+([,-]{1}[\d]+)*$', port_untagged) is None:
                port_untagged = input("Invalid enter : ")
                if port_untagged == "":
                    break
    elif vlan == 2021:
        name_vlan = "CHROMCAST"
    else:
        name_vlan = input("Enter VLAN name : ")
        while re.search(r'^[\w-]+$', name_vlan) is None:
            name_vlan = input("Enter a valid VLAN name : ")

    i = 1
    while i <= NB_Switch:
        port = 2200 + i
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=username, password=password, port=port, timeout=10)
            conn = ssh.invoke_shell()
            conn.send("\n")
            conn.send("configure terminal\n")
            time.sleep(0.5)
            conn.send("vlan {0}\n".format(vlan))
            time.sleep(0.5)
            conn.send("name {0}\n".format(name_vlan))
            time.sleep(0.5)
            conn.send("tagged all\n")
            time.sleep(0.5)
            if vlan == 2020:
                conn.send("ip address 10.200.1.{0} 255.255.0.0\n".format(i))
                time.sleep(0.5)
                conn.send("ip igmp\n")
                time.sleep(0.5)
                if i != switch_server:
                    conn.send("no ip igmp querier\n")
                    time.sleep(0.5)
                conn.send("qos priority 5\n")
                time.sleep(0.5)
                if port_untagged != "":
                    conn.send("untagged {0}\n".format(port_untagged))
                    time.sleep(0.5)                    
            conn.send("write memory\n")
            time.sleep(0.5)
            conn.send("show config status\n")
            time.sleep(0.5)
            etat = conn.recv(9999).decode("utf-8")
            if "The running configuration matches the saved configuration." in etat:
                print("Changes have been made correctly on SWITCH {0}".format(i))
            else:
                print("Error occured on SWITCH {0}".format(i))
            ssh.close()
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(str(e))
        except paramiko.ssh_exception.AuthenticationException as e:
            print(str(e))
        except paramiko.ssh_exception.socket.timeout as e:
            print(str(e))
        except paramiko.ssh_exception.SSHException as e:
            print(str(e))
        except IndexError:
            print("Unable to retrieve values correctly, please try to increase sleep when calling func recieveData")
        except Exception as e:
            print(e)
        i += 1

    reponse = ""
    while reponse != "N" and reponse != "Y":
        reponse = input("Would you like to add an other VLAN Y/N : ")
        reponse = reponse.upper()
        if reponse == "N":
            other_vlan = 0
