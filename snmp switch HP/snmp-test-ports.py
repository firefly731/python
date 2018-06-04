#!/usr/bin/python
# -*- coding: utf-8 -*-

from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
import re

OID_product  = '1.3.6.1.4.1.11.2.36.1.1.2.5.0'
OID_hostname = '1.3.6.1.2.1.1.5.0'
OID_serial = '1.3.6.1.4.1.11.2.36.1.1.2.9.0'
OID_firmware = '1.3.6.1.4.1.11.2.36.1.1.5.1.1.11.1'
OID_description = '1.3.6.1.2.1.47.1.1.1.1.2.1'
OID_ports_up = '1.3.6.1.2.1.2.2.1.8'
OID_ports_poe = '1.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1' #0 ou puissance en mW
OID_ports_poe2 = '1.3.6.1.2.1.105.1.1.1.6.1' #1 (disabled) 2 (searching) 3 (delivering power) 4 (fault) 5 (testing) 6 (other fault)
OID_MAC = '1.3.6.1.2.1.17.4.3.1.2' #mac en décimal / numéro de port
OID_MAC2 = '1.3.6.1.2.1.17.4.3.1.1' #mac en décimal / mac en héxa
OID_drop = '1.3.6.1.2.1.2.2.1.19' #['SNMPv2-SMI::mib-2.2.2.1.19.1 = 1', 'SNMPv2-SMI::mib-2.2.2.1.19.2 = 1'
OID_trafic = '1.3.6.1.2.1.2.2.1.16'#The total number of octets transmitted out  ['SNMPv2-SMI::mib-2.2.2.1.16.1 = 677788290', 'SNMPv2-SMI::mib-2.2.2.1.16.2 = 709542580'
OID_error = '1.3.6.1.2.1.2.2.1.14' #['SNMPv2-SMI::mib-2.2.2.1.14.1 = 0', 'SNMPv2-SMI::mib-2.2.2.1.14.2 = 0'

#SNMPGET
def get_value(IP, PORT, COMMUNITY, OID_ref):
    errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
    cmdgen.CommunityData(COMMUNITY),
    cmdgen.UdpTransportTarget((IP, PORT)),
    (OID_ref)
    )
    if errorIndication is None:
        return str(varBinds[0][1])
    else:
        return errorIndication

def walk_value(IP, PORT, COMMUNITY, OID_ref):
    tableau = []
    for (errorIndication,
        errorStatus,
        errorIndex,
        varBinds) in nextCmd(SnmpEngine(),
                            CommunityData(COMMUNITY),
                            UdpTransportTarget((IP, PORT)),
                            ContextData(),
                            ObjectType(ObjectIdentity(OID_ref)),
                            lexicographicMode=False):
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                tableau.append(str(varBind))
    return tableau

Switch_HP = dict()
# liste switch (modèle, nb_ports, gigabit, poe)
Switch_HP = {"J9776A":(2530, 24, True, False),
            "J9773A":(2530, 24, True, True),
            "J9779A":(2530, 24, False, True),
            "J9299A":(2520, 24, True, True),
            "J9138A":(2520, 24, False, True),
            "J9772A":(2530, 48, True, True),
            "J9781A":(2530, 48, False, False),
            "J9778A":(2530, 48, False, True),
            "J9137A":(2520, 8, False, True),
            "J9298A":(2520, 8, True, True),
            "J9783A":(2530, 8, False, False),
            "J9780A":(2530, 8, False, True),
            "J9777A":(2530, 8, True, False),
            "J9774A":(2530, 8, True, True)}


IP = input("Veuillez saisir l'IP : ")
while re.search(r'^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$', IP) is None:
    IP = input("Veuillez saisir une IP valide : ")

COMMUNITY = input("Veuillez saisir la communauté SNMP : ")

INVALID = True
while INVALID == True:
    NB_SWITCH_OU_PORT = input("Veuillez saisir le nombre de switch à interroger ou un port spécifique  : ")
    if re.search(r'^161[0-9]{2}$', NB_SWITCH_OU_PORT) is not None:
        PORT = int(NB_SWITCH_OU_PORT)
        NB_SWITCH = 1
        INVALID = False
    elif re.search(r'^[1-9][0-9]?$', NB_SWITCH_OU_PORT) is not None:
        PORT = 16101
        NB_SWITCH = int(NB_SWITCH_OU_PORT)
        INVALID = False
    else:
        print("Veuillez saisir une valeur correcte")

for n in range(NB_SWITCH):
    
    ERROR_COMM = False

    hostname = get_value(IP, PORT, COMMUNITY, OID_hostname)
    if "sw" not in str(hostname):
        print("Connexion impossible sur PORT : {0}".format(PORT))
        ERROR_COMM = True
    else:
        print("Switch {0}".format(hostname))
        Switch_key = get_value(IP, PORT, COMMUNITY, OID_product)
        if Switch_key not in Switch_HP:
            print("Une erreur s'est produite : impossible de récupérer le numéro de produit")
            ERROR_COMM = True
        else:
            PORT_LINK = walk_value(IP, PORT, COMMUNITY, OID_ports_up)
            #['SNMPv2-SMI::mib-2.2.2.1.8.1 = 1', 'SNMPv2-SMI::mib-2.2.2.1.8.2 = 1'   ==>   1 port up, 2 port down
            if "2.2.2.1.8" not in str(PORT_LINK):
                print("Une erreur s'est produite : impossible de récupérer l'état des liens")
                ERROR_COMM = True
            else:
                PORT_MAC = walk_value(IP, PORT, COMMUNITY, OID_MAC)
                #SNMPv2-SMI::mib-2.17.4.3.1.2.232.57.53.241.205.183 = 2', 'SNMPv2-SMI::mib-2.17.4.3.1.2.232.57.53.241.205.185 = 4' ==>  si pas de correspondance sur le port recherché il n'y a pas de MAC
                if "2.17.4.3.1.2" not in str(PORT_MAC):
                    print("Une erreur s'est produite : impossible de récupérer la table ARP")
                    ERROR_COMM = True
                else:
                    if Switch_HP[Switch_key][3] == True: #test si switch est POE
                        PORT_POE = walk_value(IP, PORT, COMMUNITY, OID_ports_poe)
                        #['SNMPv2-SMI::enterprises.11.2.14.11.1.9.1.1.1.3.1.1 = 5301', 'SNMPv2-SMI::enterprises.11.2.14.11.1.9.1.1.1.3.1.2 = 5385'   ==>  0 pas de POE sinon POE
                        if "11.2.14.11.1.9.1.1.1.3.1" not in str(PORT_POE):
                            print("Une erreur s'est produite : impossible de récupérer l'état du POE")
                            ERROR_COMM = True

    PORT += 1

    ERROR = False

    if ERROR_COMM == False:
        NB_PORT = Switch_HP[Switch_key][1]
        for i in range(NB_PORT):
            link_on = re.search(r'({0} = )(\d)'.format(i+1), str(PORT_LINK))
            mac_on = re.search(r'( = )({0})'.format(i+1), str(PORT_MAC))
            if int(link_on.group(2)) == 1 and mac_on is None:
                print("LINK activé mais pas de MAC détectée sur port {0}".format(i+1))
                ERROR = True
            if Switch_HP[Switch_key][3] == True: #test si switch est POE 
                poe_on = re.search(r'({0} = )(\d*)'.format(i+1), str(PORT_POE))
                if int(poe_on.group(2)) != 0 and int(link_on.group(2)) == 2:
                    print("POE activé mais pas de LINK détecté sur port {0}".format(i+1))
                    ERROR = True
                if int(poe_on.group(2)) != 0 and mac_on is None:
                    print("POE activé mais pas de MAC détectée sur port {0}".format(i+1))
                    ERROR = True
        if ERROR == False:
            print("Aucun problème détecté")

                
"""
reste counters pas de link
ports error
modifier programme avec OID_ports_poe2 (+ simple)
test site 11618 switch 4 erreur port 13 ...
amélioration des test imbriqué switch case ...
test avec des get par port pour voir si plus rapide que des walk
"""

