#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1'

import os, sys, string, telnetlib,re
import json
from getpass import getpass
from time import time


from pymongo import Connection


##from majlistemodemsjson import MajListeModemsJson
class InventaireDslam:
    """

    """

    def __init__(self, user_list, cmd_list, **kw):

        self.timeout = kw.get('timeout', 20)
        self.command_prompt = ">"
        self.passwd = {}
	self.user_list=user_list
	self.cmd_list=cmd_list
	self.mdp="ci6kcapass"
	self.connection = Connection()
	self.db = self.connection.pacsdb
	self.collection = self.db.modems
	
	

    def inventaire(self,host_list):

	for user in self.user_list:

	    self.passwd[user] = self.mdp

	
	for host in host_list:

	    """ on passe tous les hosts a la moulinette """

	    dslam=host[-2:]

	    
	    pinghost = os.system("ping -c 1 "+host)

	    if pinghost == 0:

		self.telnet = telnetlib.Telnet()
		print 'host',host
		try :
		    self.telnet.open(host,23,10)
		    portDslam = self.action(self.user_list[0], self.cmd_list,host)

		    
		    self.telnet.close()


		except Exception, err:
		    print 'eerro'
		 

		parse=self.parseportDSLAM(portDslam)

		parse["DSLAM"]=dslam
		
		self.ecrirebase(parse)
		
		

    def action(self, user, cmd_list,host):

	"""
	"""

	# initialisation de la session telnet
        t = self.telnet

	responses = t.read_some()

	

	# Premierement : teste si il y a une demande de login
	if string.count(responses, "User name:"):
		t.write("admin\n")
		
		# s'il y a un login alors c'est un T1A et le prompte de l'interpréteur de commande est #
		self.command_prompt=">"

		# On attends la demande du mot de passe
		password_prompt = "Password:"
		response = t.read_until(password_prompt, 10)

		if string.count(response, password_prompt):

			t.write("%s\n" % self.mdp)
		else:
		    return 0


	# On attent le prompt de l'interpréteur de commande
        response = t.read_until(self.command_prompt, 5)
        if not string.count(response, self.command_prompt):
            return 0

	# on est connecte on commence de lancer les commandes
        for cmd in cmd_list:

	    t.write("%s\n" % cmd)

	    response = t.read_until(self.command_prompt, self.timeout)
	    t.write("n\n")
            response = response + t.read_until(self.command_prompt, self.timeout)

	# on oublie pas de fermer la session sur le DSLAM
	t.write('exit')

	
	return response


    def parseportDSLAM(self,reponse):

	""" Parser le tableau du dslam """
	
	reponse = reponse.split('Port:')
	macport={}
	
	for a in reponse :

	    if a.startswith(' Enet') or a.startswith(' statistics'):

		pass

	    else :

		a=a.replace(':','')
		a=a.replace('\r','')
		a=a.replace('index  vid mac','')
		a=a.replace('----- ---- -----------------','')
		#print 'a',a
		a=a.split('\n')
		
		b=[]
		
		b.append(a[0].replace(' ',''))

		for c in a:
		    if len(c)>3:

			c=c[8:]
			c=c.split(' ')
			if c[0]=='50' :
			    b.append(c[1])
			    macport[b[0]]=b[1]


	return macport



    def ecrirebase(self,portsdslam):

	""" Mise à jour de la base """
	
	dslam=int(portsdslam["DSLAM"])
	print dslam
	for port in portsdslam:
	    
	    mac=portsdslam[port]
	    mac=mac.upper()
	    if len(mac)==12:
	    

		print 'mac',mac,'\n'
		
		try :

		    modemindb = self.collection.find_one({"mac":"%s" %mac})
		    #print 'modem trouve',modemindb
		    modemindbid = modemindb['_id']
		    #print "dslam: %s portdslam : %s" %(dslam,port)
		    self.collection.update({"_id": modemindbid},{"$set":{"dslam":dslam ,"portdslam":int(port)}})

		
		except :

		    print 'ERROR'





if __name__ == '__main__':
    
    

    cmd_list = ["statistics mac"]
    user_list = ["admin"]
    # Liste DSLAM
    host_list = ["192.168.1.101","192.168.1.102","192.168.1.103","192.168.1.104","192.168.1.105","192.168.1.106","192.168.1.107","192.168.1.108","192.168.1.109","192.168.1.110","192.168.1.111","192.168.1.112","192.168.1.113","192.168.1.114","192.168.1.115","192.168.1.116","192.168.1.117","192.168.1.118"]#,"192.168.1.102","192.168.1.103","192.168.1.104","192.168.1.105","192.168.1.106","192.168.1.108","192.168.1.109","192.168.1.110","192.168.1.111","192.168.1.112","192.168.1.113","192.168.1.114","192.168.1.115","192.168.1.116","192.168.1.117","192.168.1.118"

    # enfin lancement de l'inventaire 
    invDslam = InventaireDslam(user_list, cmd_list,)
    invDslam.inventaire(host_list)
