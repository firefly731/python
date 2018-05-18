#!/usr/bin/python
# -*- coding: utf-8 -*-

from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

import re
import os


def write_file(donnees):
    try:
        with open('switch-info.txt', 'w', encoding='utf-8') as f:
            f.write(donnees)
    except Exception as inst:
        print(inst)

def append_file(donnees):
    try:
        with open('switch-info.txt', 'a', encoding='utf-8') as f:
            f.write(donnees)
    except Exception as inst:
        print(inst)

def get_value(IP, PORT, COMMUNITY, OID_ref):
    errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
    cmdgen.CommunityData(COMMUNITY),
    cmdgen.UdpTransportTarget((IP, PORT)),
    (OID_ref)
    )
    return str(varBinds[0][1])

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

IP = '172.20.1.36'
PORT = 16109
COMMUNITY = 'uds7wVvB'
OID_hostname = '1.3.6.1.2.1.1.5.0'
OID_serial = '1.3.6.1.4.1.11.2.36.1.1.2.9.0'
OID_firmware = '1.3.6.1.4.1.11.2.36.1.1.5.1.1.11.1'
OID_product  = '1.3.6.1.4.1.11.2.36.1.1.2.5.0'
OID_description = '1.3.6.1.2.1.47.1.1.1.1.2.1'
OID_ports = '1.3.111.2.802.1.1.2.1.1.1.1.3.1'
OID_ports_up = '1.3.6.1.2.1.2.2.1.8'
OID_ports_poe = '1.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3'
OID_ports_vlan = '1.3.6.1.2.1.17.7.1.4.5.1.1'

Swtich = []

Swtich.append(('Description', get_value(IP, PORT, COMMUNITY, OID_description)))
Swtich.append(('Hostname', get_value(IP, PORT, COMMUNITY, OID_hostname)))
Swtich.append(('Serial', get_value(IP, PORT, COMMUNITY, OID_serial)))
Swtich.append(('Firmware', get_value(IP, PORT, COMMUNITY, OID_firmware)))

"""
nb_ports = int(get_value(IP, PORT, COMMUNITY, OID_ports))
ports_count = 0
for e,i in enumerate(walk_value(IP, PORT, COMMUNITY, OID_ports_up)):
    if i[-1] == '1' and e < nb_ports:
    #if i[-1] == '1' and e < 28:
        ports_count += 1
    else:
        pass
Swtich.append(('Nombre de ports utilisés', ports_count))
"""
ports_count = 0
for i in walk_value(IP, PORT, COMMUNITY, OID_ports_poe):
    if i[-2:] != ' 0':
        ports_count += 1
    else:
        pass
Swtich.append(('Nombre de ports POE utilisés', ports_count))

POE_libre = 24 - ports_count

ports_count = 0
for i in walk_value(IP, PORT, COMMUNITY, OID_ports_vlan):
    if i[-4:] == '3501':
        ports_count += 1
    else:
        pass

POE_libre -= ports_count
Swtich.append(('Nombre de ports POE libres', POE_libre))
Swtich.append(('Nombre de ports reservés pour séminaire', ports_count))


donnees = ""
for a,b in Swtich:
    donnees += "{} : {}\n".format(a,b)

write_file(donnees)


"""


"""