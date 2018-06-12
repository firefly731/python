#!/usr/bin/python
# -*- coding: utf-8 -*-


import paramiko #library for ssh connection
import time


hostname = '172.20.0.36'
username = 'jdumoulin'
password = 'Ihavufak03'
port = '2201'

def recieveData():
    tCheck = 0
    while not conn.recv_ready():
        time.sleep(2)
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
                del(liste[i][:index])
        except:
            pass
    liste = [x for x in liste if x[0].isdigit()]
    return liste

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

    for i in interfaces:
        print(i)
    #print(interfaces[11])

    print("")

    conn.send("show interfaces brief\n")
    conn.send(" ")
    recieveData()
    interfaces_brief = formattedData(conn.recv(9999).decode("utf-8"))
    #['1', '100/1000T',       'No',          'Yes',   'Down', '1000FDx', 'MDI',      'off']
    #[Port, Type,        Intrusion Alert,   Enabled , Status,    Mode,   MDI Mode, Flow Ctrl]

    for i in interfaces_brief:
        print(i)
    #print(interfaces_brief[20])
    
    print("")

    conn.send("show power-over-ethernet brief\n")
    conn.send(" ")
    recieveData()
    interfaces_poe = formattedData(conn.recv(9999).decode("utf-8"))
    #['1',      'Yes',     'low',       'off',       'usage',       'usage',     '0.0', 'W',   '0.0', 'W',  'Searching', '0', '-']
    #[Port, Pwr enabled, Priority, Pre-std detect, Alloc config, Alloc actual,  Pwr reserved,  Pwr draw',    PoE status, '0', '-']

    if interfaces_poe:
        for i in interfaces_poe:
            print(i)
        #print(interfaces_poe[5])
    else:
        print("switch non poe")
    
    ssh.close()
except paramiko.ssh_exception.NoValidConnectionsError as e:
    print(str(e))
except paramiko.ssh_exception.AuthenticationException as e:
    print(str(e))
except paramiko.ssh_exception.socket.timeout as e:
    print(str(e))
except paramiko.ssh_exception.SSHException as e:
    print(str(e))
