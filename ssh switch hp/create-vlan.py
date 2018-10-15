#!/usr/bin/python3.5
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

nb = False
while nb == False:
    vlan = input("Enter the number of VLAN : ")
    try:
        vlan = int(vlan)
    except ValueError:
        print("Please enter a number")
    else:
        nb = True

i = 1
while i <= NB_Switch:
    port = 2200 + i
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, port=port, timeout=10)

        conn = ssh.invoke_shell()
        conn.send("\n")
        recieveData()
        conn.recv(9999)
        conn.send("show lldp info local-device\n")
        conn.send(" ")
        recieveData()
        nbport = conn.recv(9999).decode("utf-8").split("\n")
        nbport = nbport[-2].strip().split(" ")[-1]
        conn.send("configure terminal\n")
        time.sleep(0.5)
        conn.send("vlan {0}\n".format(vlan))
        time.sleep(0.5)
        conn.send("tagged 1-{0}\n".format(nbport))
        time.sleep(0.5)
        conn.send("write memory\n")
        time.sleep(0.5)
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

input("Enter enter to quit ....")