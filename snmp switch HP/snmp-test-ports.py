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
OID_MAC = '1.3.6.1.2.1.17.4.3.1.2'

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
SNMPv2-SMI::mib-2.17.4.3.1.2.232.57.53.241.205.183 = 2', 'SNMPv2-SMI::mib-2.17.4.3.1.2.232.57.53.241.205.185 = 4'
"""
PORT_LINK = walk_value(IP, PORT, COMMUNITY, OID_ports_up)
"""
recup
iso.3.6.1.2.1.2.2.1.8.1 = INTEGER: 1 (UP)
iso.3.6.1.2.1.2.2.1.8.2 = INTEGER: 1
iso.3.6.1.2.1.2.2.1.8.3 = INTEGER: 1
iso.3.6.1.2.1.2.2.1.8.4 = INTEGER: 1
iso.3.6.1.2.1.2.2.1.8.5 = INTEGER: 2 (DOWN)
iso.3.6.1.2.1.2.2.1.8.6 = INTEGER: 2
iso.3.6.1.2.1.2.2.1.8.7 = INTEGER: 2
iso.3.6.1.2.1.2.2.1.8.8 = INTEGER: 2
"""
PORT_POE = walk_value(IP, PORT, COMMUNITY, OID_ports_poe)
"""
recup
iso.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1.1 = INTEGER: 5301 (POE)
iso.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1.2 = INTEGER: 5385
iso.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1.3 = INTEGER: 5257
iso.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1.4 = INTEGER: 5222
iso.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1.5 = INTEGER: 0 (NO POE)
iso.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3.1.6 = INTEGER: 0

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
            

# mac table to port : 1.3.6.1.2.1.17.4.3.1.2
# mac table hexa : 1.3.6.1.2.1.17.4.3.1.1