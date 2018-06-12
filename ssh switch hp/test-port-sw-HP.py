#!/usr/bin/python
# -*- coding: utf-8 -*-


import paramiko #library for ssh connection
import time
import re
import getpass


#hostname = '172.20.0.36'
#username = 'jdumoulin'
#password = 'Ihavufak03'
#port = '2201'

def recieveData(sleep=2):
    tCheck = 0
    while not conn.recv_ready():
        time.sleep(sleep)
        tCheck+=1
        if tCheck >=10:
            print("time out")

def formattedData(recvData):
    liste = list()
    recvData = str(recvData).split("\n")
    for lines in recvData:
        e = lines.split(" ")
        e = [i for i in e if i != '' and i != '\r' and i != '|'] #remove undesirable elements in list
        if e:
            liste.append(e)
    for i,e in enumerate(liste):
        try:
            if not e[0].isdigit():
                num_port = int(liste[i-1][0]) + 1 #retrieve port number line above then add 1
                index = e.index(str(num_port)) #check if value is found in line
                del(liste[i][:index]) #delete all elements before port number
        except:
            pass
    liste = [x for x in liste if x[0].isdigit()]
    return liste

hostname = input("Enter an IP address : ")
while re.search(r'^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$', hostname) is None:
    hostname = input("Please enter a valid IP address : ")

INVALID = True
while INVALID == True:
    NB_Switch_OU_Port = input("Enter the number of switch to check or a specific port (2201, 2202, ...)  : ")
    if re.search(r'^22[0-9]{2}$', NB_Switch_OU_Port) is not None: #check if port is like 22XX then check one switch
        port = int(NB_Switch_OU_Port)
        NB_Switch = 1
        INVALID = False
        print("\n")
    elif re.search(r'^[1-9][0-9]?$', NB_Switch_OU_Port) is not None: #if input is between 1 and 99 then check on multiple switch
        port = 2201
        NB_Switch = int(NB_Switch_OU_Port)
        INVALID = False
        print("\n")
    else:
        print("Please enter a valid input")

username = input("Login: ")
password = getpass.getpass(prompt='Password: ')

for n in range(NB_Switch):

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, port=port, timeout=10)
        conn = ssh.invoke_shell()
        conn.send("\n")
        recieveData()
        conn.recv(9999)

        conn.send("show interfaces\n")
        conn.send(" ")
        recieveData()
        interfaces = formattedData(conn.recv(9999).decode("utf-8"))
        #['1',    '9050',         '41',       '3',      '0',    'off']
        #[Port, Total Bytes, Total Frames, Errors Rx, Drops Tx, Flow Ctrl]

        conn.send("show interfaces brief\n")
        conn.send(" ")
        recieveData()
        interfaces_brief = formattedData(conn.recv(9999).decode("utf-8"))
        #['1', '100/1000T',       'No',          'Yes',   'Down', '1000FDx', 'MDI',      'off']
        #[Port, Type,        Intrusion Alert,   Enabled , Status,    Mode,   MDI Mode, Flow Ctrl]

        conn.send("show power-over-ethernet brief\n")
        conn.send(" ")
        recieveData()
        interfaces_poe = formattedData(conn.recv(9999).decode("utf-8"))
        #['1',      'Yes',     'low',       'off',       'usage',       'usage',     '0.0', 'W',   '0.0', 'W',  'Searching', '0', '-']
        #[Port, Pwr enabled, Priority, Pre-std detect, Alloc config, Alloc actual,  Pwr reserved,  Pwr draw',    PoE status, '0', '-']

        NB_port = len(interfaces)
        NB_port_poe = len(interfaces_poe)
        ERROR = False

        for nb in range(NB_port):
            
            conn.send("show mac-address {}\n".format(nb+1))
            recieveData(0.5)
            MAC = conn.recv(9999).decode("utf-8").split("\n")
            print(nb+1)
            print(MAC[5])
            


        ssh.close()
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(str(e))
    except paramiko.ssh_exception.AuthenticationException as e:
        print(str(e))
    except paramiko.ssh_exception.socket.timeout as e:
        print(str(e))
    except paramiko.ssh_exception.SSHException as e:
        print(str(e))
"""
            if interfaces_brief[nb][4] == "up" and str(i+1) not in mac_on:
                print("LINK activé mais pas de MAC détectée sur port {0}".format(i+1))
                ERROR = True
                drop_on = session.get("{0}.{1}".format(OID_drop, (i+1))).value
                if int(drop_on) != 0:
                    print("DROP détecté sur port {0}".format(i+1))
                    ERROR = True
                error_on = session.get("{0}.{1}".format(OID_error, (i+1))).value
                if int(error_on) != 0:
                    print("ERREUR détecté sur port {0}".format(i+1))
                    ERROR = True
                if Switch_HP[Switch_key][3] == True: #test si switch est POE 
                    poe_on = session.get("{0}.{1}".format(OID_ports_poe, (i+1))).value
                    if int(poe_on) != 0 and int(link_on) == 2:
                        print("POE activé mais pas de LINK détecté sur port {0}".format(i+1))
                        ERROR = True
                    if int(poe_on) != 0 and str(i+1) not in mac_on:
                        print("POE activé mais pas de MAC détectée sur port {0}".format(i+1))
                        ERROR = True

            if ERROR == False:
                print("Aucun problème détecté")
        print("\n")        
        port += 1    
"""