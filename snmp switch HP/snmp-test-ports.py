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
OID_ports_poe = '1.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3'
OID_MAC = '1.3.6.1.2.1.17.4.3.1.2' #mac en décimal / numéro de port
OID_MAC2 = '1.3.6.1.2.1.17.4.3.1.1' #mac en décimal / mac en héxa

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

PORT = 16101

IP = input("Veuillez saisir l'IP : ")
while re.search(r'^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$', IP) is None:
    IP = input("Veuillez saisir une IP valide : ")

COMMUNITY = input("Veuillez saisir la communauté SNMP : ")

NB_SWITCH = input("Veuillez saisir le nombre de SWITCH : ")
while re.search(r'^[1-9][0-9]?$', NB_SWITCH) is None:
    NB_SWITCH = input("Veuillez saisir un nombre valide : ")

NB_SWITCH = int(NB_SWITCH)

PORT_MAC = walk_value(IP, PORT, COMMUNITY, OID_MAC)
"""
recup
SNMPv2-SMI::mib-2.17.4.3.1.2.232.57.53.241.205.183 = 2', 'SNMPv2-SMI::mib-2.17.4.3.1.2.232.57.53.241.205.185 = 4' ==>  si pas de correspondance sur le port recherché il n'y a pas de MAC
"""
PORT_LINK = walk_value(IP, PORT, COMMUNITY, OID_ports_up)
"""
recup
['SNMPv2-SMI::mib-2.2.2.1.8.1 = 1', 'SNMPv2-SMI::mib-2.2.2.1.8.2 = 1'   ==>   1 port up, 2 port down
"""
PORT_POE = walk_value(IP, PORT, COMMUNITY, OID_ports_poe)
"""
recup
['SNMPv2-SMI::enterprises.11.2.14.11.1.9.1.1.1.3.1.1 = 5301', 'SNMPv2-SMI::enterprises.11.2.14.11.1.9.1.1.1.3.1.2 = 5385'   ==>  0 pas de POE sinon POE
"""
while NB_SWITCH != 0:
    Switch_key = get_value(IP, PORT, COMMUNITY, OID_product)
    PORT += 1
    NB_SWITCH -= 1
    if "J9" not in str(Switch_key):
        print("Une erreur s'est produite : ")
        print(Switch_key)
    else:
        NB_PORT = Switch_HP[Switch_key][1]
        for i in range(NB_PORT):
            poe_on = re.search(r'({0} = )(\d*)'.format(i+1), str(PORT_POE))
            link_on = re.search(r'({0} = )(\d)'.format(i+1), str(PORT_LINK))
            mac_on = re.search(r'( = )({0})'.format(i+1), str(PORT_MAC))
            if int(poe_on.group(2)) != 0 and int(link_on.group(2)) == 2:
                print("POE activé mais pas de LINK détecté sur port {0}".format(i+1))
            elif int(poe_on.group(2)) != 0 and mac_on is None:
                print("POE activé mais pas de MAC détectée sur port {0}".format(i+1))
            else:
                print("Aucun problème détecté")
                
"""
            if int(poe_on.group(2)) == 0:
                print("poe désactivé port {0}".format(i+1))
            else:
                print("poe activé port {0}".format(i+1))
            if int(link_on.group(2)) == 1:
                print("link ok port {0}".format(i+1))
            else:
                print("link ko port {0}".format(i+1))
            if mac_on is None:
                print("pas de mac détecté port {0}".format(i+1))
            else:
                print("mac détecté port {0}".format(i+1))
"""

