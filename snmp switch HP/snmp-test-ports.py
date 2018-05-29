#!/usr/bin/python
# -*- coding: utf-8 -*-

from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
import re

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

#SNMPWALK
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
PORT = 16101
COMMUNITY = 'uds7wVvB'
OID_hostname = '1.3.6.1.2.1.1.5.0'
OID_serial = '1.3.6.1.4.1.11.2.36.1.1.2.9.0'
OID_firmware = '1.3.6.1.4.1.11.2.36.1.1.5.1.1.11.1'
OID_description = '1.3.6.1.2.1.47.1.1.1.1.2.1'
OID_ports_up = '1.3.6.1.2.1.2.2.1.8'
OID_ports_poe = '1.3.6.1.4.1.11.2.14.11.1.9.1.1.1.3'

Description = get_value(IP, PORT, COMMUNITY, OID_description).split()
#On enlève la valeur 'Switch' dans la liste pour avoir la même liste avec les 2520 et les 2530
"""
Exemple de valeurs récupérées :
HP J9776A 2530-24G Switch (Formerly ProCurve)
HP J9773A 2530-24G-PoEP Switch (Formerly ProCurve)
HP J9779A 2530-24-PoEP Switch (Formerly ProCurve)
HP J9299A Switch 2520G-24-PoE (Formerly ProCurve)
HP J9138A Switch 2520-24-PoE (Formerly ProCurve)
HP J9772A 2530-48G-PoEP Switch (Formerly ProCurve)
"""

Description.remove('Switch')

Marque, Produit, Modele, *Junk = Description

#Avec le modèle on récupère le nombre de ports et si le switch est POE
NbPorts = int("".join(re.findall(r'[0-9]', Modele.split('-')[1])))
if 'PoE' in Modele:
    POE = True
else:
    POE = False

Serial = get_value(IP, PORT, COMMUNITY, OID_serial)
Firmware = get_value(IP, PORT, COMMUNITY, OID_firmware)
Hostname = get_value(IP, PORT, COMMUNITY, OID_hostname)

#On récupère la liste du statut des ports UP ou DOWN, hors ports d'uplink
PortUP = walk_value(IP, PORT, COMMUNITY, OID_ports_up)
NbPortsUP = 0
NbPortsDOWN = 0
for i in PortUP:
    if NbPorts > 0:
        if int(i.split()[-1]) == 1:
            NbPortsUP += 1
        else:
            NbPortsDOWN += 1
    NbPorts -= 1

#On récupère la liste des ports qui délivrent du POE
PortPOE = walk_value(IP, PORT, COMMUNITY, OID_ports_poe)
NbPortsPOE = 0
for i in PortPOE:
    if int(i.split()[-1]) != 0:
        NbPortsPOE += 1
print(NbPortsPOE)