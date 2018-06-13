#!/usr/bin/python
# -*- coding: utf-8 -*-


import paramiko #library for ssh connection
import time
import re
import getpass

def recieveData(sleep=4): #change sleep value if needed
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
    NB_Switch_OU_Port = input("Enter the number of switch to check or a specific port (ex : 22XX)  : ")
    if re.search(r'^22[0-9]{2}$', NB_Switch_OU_Port) is not None: #check if port is like 22XX then check one switch
        port = int(NB_Switch_OU_Port)
        NB_Switch = 1
        INVALID = False
        print("")
    elif re.search(r'^[1-9][0-9]?$', NB_Switch_OU_Port) is not None: #if input is between 1 and 99 then check on multiple switch
        port = 2201
        NB_Switch = int(NB_Switch_OU_Port)
        INVALID = False
        print("")
    else:
        print("Please enter a valid input")

username = input("Login: ")
password = getpass.getpass(prompt='Password: ')
print("")

for n in range(NB_Switch):

    try:
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, port=port, timeout=10)

        conn = ssh.invoke_shell()
        conn.send("\n")
        recieveData()
        name = conn.recv(9999).decode("utf-8").split("\n")
        name = name[-1]
        print(name.strip())
        print("")

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
            recieveData(1.5) #change sleep value if needed
            MAC = conn.recv(9999).decode("utf-8").split("\n")
            if interfaces_brief[nb][4] == "Down" and interfaces[nb][1] != "0":
                print("LINK DOWN but traffic was detected on port {0}".format(nb+1))
                ERROR = True
            if interfaces_brief[nb][4] == "Up" and MAC[5].strip() == "":
                print("LINK UP but no mac address on port {0}".format(nb+1))
                ERROR = True
            if interfaces[nb][4] != "0":
                    print("DROP detected on port {0}".format(nb+1))
                    ERROR = True
            if interfaces[nb][3] != "0":
                    print("ERROR detected on port {0}".format(nb+1))
                    ERROR = True
            if interfaces_poe and nb+1 <= len(interfaces_poe): #check if switch is POE and avoid link port
                if "Delivering" in interfaces_poe[nb] and interfaces_brief[nb][4] == "Down":
                        print("POE detected but no LINK on port {0}".format(nb+1))
                        ERROR = True
                if "Delivering" in interfaces_poe[nb] and MAC[5].strip() == "":
                        print("POE detected but no MAC address on port {0}".format(nb+1))
                        ERROR = True        
        if ERROR == False:
            print("No problem detected")
        print("\n")        
        port += 1

        print("")    

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
    except:
        print("unknown error occured")
