#!/usr/bin/python
# -*- coding: utf-8 -*-

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

class SNMPClient:
    # This is the SNMPClient constructor
    def __init__(self, host, port=161, community='public'):
        
        self.host = host
        self.port = port
        self.community = community
 
    def snmpget(self, oid, *more_oids):
        
        from pysnmp.entity.rfc3413.oneliner import cmdgen
 
        cmdGen = cmdgen.CommandGenerator()
        
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, self.port)),
            oid,
            *more_oids
        )
 
        # Predefine our results list    
        results = []
 
        # Check for errors and print out results
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                for name, val in varBinds:
                    results.append( val )
 
            if len(results) == 1:
                return results[0]
            else:
                return results

    def snmpwalk(self, oid):
        
        from pysnmp.entity.rfc3413.oneliner import cmdgen
     
        cmdGen = cmdgen.CommandGenerator()
        
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, self.port)),
            oid
        )
 
        # Predefine our results list    
        results = []
 
        # Check for errors and print out results
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                for varBind1, *varBind2 in varBinds:
                    results.append(str(varBind1))
 
            if len(results) == 1:
                return results[0]
            else:
                return results

IP = input("Veuillez saisir l'IP : ")
while re.search(r'^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$', IP) is None:
    IP = input("Veuillez saisir une IP valide : ")

COMMUNITY = input("Veuillez saisir la communauté SNMP : ")

INVALID = True
while INVALID == True:
    NB_SWITCH_OU_PORT = input("Veuillez saisir le nombre de switch à interroger ou un numéro de port (16101, 16104, ...)  : ")
    if re.search(r'^161[0-9]{2}$', NB_SWITCH_OU_PORT) is not None:
        PORT = int(NB_SWITCH_OU_PORT)
        NB_SWITCH = 1
        INVALID = False
        print("\n")
    elif re.search(r'^[1-9][0-9]?$', NB_SWITCH_OU_PORT) is not None:
        PORT = 16101
        NB_SWITCH = int(NB_SWITCH_OU_PORT)
        INVALID = False
        print("\n")
    else:
        print("Veuillez saisir une valeur correcte")

for n in range(NB_SWITCH):
    
    session = SNMPClient(IP, PORT, COMMUNITY)
    ERROR_COMM = False

    hostname = session.snmpget(OID_hostname)
    if hostname:
        print("Switch {0}".format(hostname))
    else:
        print("Connexion impossible sur PORT : {0}".format(PORT))
        ERROR_COMM = True
        
    if ERROR_COMM == False:
        Switch_key = session.snmpget(OID_product)
        if str(Switch_key) not in Switch_HP:
            print("Une erreur s'est produite : impossible de récupérer le numéro de produit")
            ERROR_COMM = True

    if ERROR_COMM == False:
        PORT_MAC = session.snmpwalk(OID_MAC)
        if "2.17.4.3.1.2" not in str(PORT_MAC):
            print("Une erreur s'est produite : impossible de récupérer la table ARP")
            ERROR_COMM = True

    if ERROR_COMM == False:
        ERROR = False
        NB_PORT = Switch_HP[str(Switch_key)][1]
        LIST_OIDport = []
        LIST_OIDdrop = []
        LIST_OIDerreur = []
        LIST_OIDpoe = []
        LIST_port = []
        LIST_drop = []
        LIST_erreur = []
        LIST_poe = []

        for i in range(NB_PORT):
            LIST_OIDport.append("{0}.{1}".format(OID_ports_up, (i+1)))
            LIST_OIDdrop.append("{0}.{1}".format(OID_drop, i+1))
            LIST_OIDerreur.append("{0}.{1}".format(OID_error, i+1))
            LIST_OIDpoe.append("{0}.{1}".format(OID_ports_poe, i+1))
        
        LIST_port = session.snmpget(*LIST_OIDport)
        LIST_drop = session.snmpget(*LIST_OIDdrop)
        LIST_erreur = session.snmpget(*LIST_OIDerreur)
        if Switch_HP[str(Switch_key)][3] == True: #test si switch est POE
            LIST_poe = session.snmpget(*LIST_OIDpoe)

        for i in range(NB_PORT):
            mac_on = re.search(r'( = )({0})'.format(i+1), str(PORT_MAC))
            if int(LIST_port[i]) == 1 and mac_on is None:
                print("LINK activé mais pas de MAC détectée sur port {0}".format(i+1))
                ERROR = True
            if int(LIST_drop[i]) != 0:
                print("DROP détecté sur port {0}".format(i+1))
                ERROR = True
            if int(LIST_erreur[i]) != 0:
                print("ERREUR détecté sur port {0}".format(i+1))
                ERROR = True
            if Switch_HP[str(Switch_key)][3] == True: #test si switch est POE 
                if int(LIST_poe[i]) != 0 and int(LIST_port[i]) == 2:
                    print("POE activé mais pas de LINK détecté sur port {0}".format(i+1))
                    ERROR = True
                if int(LIST_poe[i]) != 0 and mac_on is None:
                    print("POE activé mais pas de MAC détectée sur port {0}".format(i+1))
                    ERROR = True

        if ERROR == False:
            print("Aucun problème détecté")
    print("\n")        
    PORT += 1   

"""
modifier programme avec OID_ports_poe2 (+ simple)
test site 11618 switch 4 erreur port 13 ...
test counters
"""

