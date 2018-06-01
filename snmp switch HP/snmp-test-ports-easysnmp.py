#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from easysnmp import Session

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
    
    session = Session(hostname=IP, community=COMMUNITY, version=2, remote_port=PORT)
    PORT += 1    
    ERROR_COMM = False

    hostname = session.get(OID_hostname).value
    if "sw" not in str(hostname):
        print("Connexion impossible sur PORT : {0}".format(PORT))
        ERROR_COMM = True
    else:
        print("Switch {0}".format(hostname))

    if ERROR_COMM == False:
        Switch_key = session.get(OID_product).value
        if Switch_key not in Switch_HP:
            print("Une erreur s'est produite : impossible de récupérer le numéro de produit")
            ERROR_COMM = True

    if ERROR_COMM == False:
        PORT_MAC = session.walk(OID_MAC)
        mac_on = []
        for i in PORT_MAC:
            mac_on.append(i.value)
        if not PORT_MAC:
            print("Une erreur s'est produite : impossible de récupérer la table ARP")
            ERROR_COMM = True

    ERROR = False

    if ERROR_COMM == False:
        NB_PORT = Switch_HP[Switch_key][1]
        for i in range(NB_PORT):
            link_on = session.get("{0}.{1}".format(OID_ports_up, (i+1))).value
            if int(link_on) == 1 and str(i+1) not in mac_on:
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

"""
reste counters pas de link
modifier programme avec OID_ports_poe2 (+ simple)
test site 11618 switch 4 erreur port 13 ...
"""

