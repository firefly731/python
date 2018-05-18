 #!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.2'

import os, sys, string, telnetlib,re
import json
from getpass import getpass
from time import sleep
from time import time
from journal import Journal
from conf import Conf
import shelve
from pymongo import Connection


##from majlistemodemsjson import MajListeModemsJson
class AutoTelnet:
    """
    inventaire.AutoTelnet : Class qui va faire l'inventaire des modems,
    Elle prends comme argument la liste des utilisateurs,  la liste des commandes et la liste des ip a tester
    les fonctions :
    def inventaire
    def action
    def ecrirebase
    def parseSysatsh
    def modemJson
    def deflease
    03/09/14 : Ajout de la detection des TG582N

    """
    
    def __init__(self, user_list, cmd_list, **kw):

	self.host = '10.5.20.83'
	self.timeout = kw.get('timeout', 60)
	self.command_prompt = "# "
	self.passwd = {}
	self.modemInfo = {}
	self.comptemodem=0
	self.user_list=user_list
	self.cmd_list=cmd_list
	self.conf=Conf()
	self.mdp=self.conf.telnetMdp
	self.database=self.conf.database
	self.connection = Connection()

	self.db = self.connection.pacsdb
	self.collection = self.db.modems
	self.modemmodel= ""
	
	

    def inventaire(self,host_list):

	for user in self.user_list:

	    self.passwd[user] = self.mdp

	#self.base=shelve.open(self.database)
	
	for host in host_list:

	    """ on passe tous les hosts a la moulinette """

	    self.modemInfo = {}
	    
	    pinghost = os.system("ping -c 1 "+host)

	    if pinghost == 0:

		self.telnet = telnetlib.Telnet()
		print 'host',host
		try :
		    self.telnet.open(host,23,10)
		    ok = self.action(self.user_list[0], self.cmd_list,host)
		    if not ok:

			print "pas de login:", user
			self.telnet.close()
			sleep(2)
		except Exception, err:
		    print 'eerro'
		#self.telnet.set_debuglevel(3)

		#logprompt = self.defloginprompt(host)
		#logprompt="login:"
		
		
		
		
		


#########Journal().ecrireJournal("INFO","Inventaire realise sans erreur - %s modems repertories " %str(self.comptemodem))
	#self.journal("INFO","Inventaire realise sans erreur - %s modems repertories " %str(self.comptemodem)) 

	# Et finalement on verifie que la liste des modems est à jour
	#MajListeModemsJson()

    def action(self, user, cmd_list,host):

	"""
	fonction qui va se connecter au modem et passer les commandes.
	Elle prends comme argument :
	user : le login a utiliser -> ne sera pas utilise, les variable seron utilises dans definie dans conf
	cmd_list -> la liste des commandes a passer aux modems pour l'inventaire ca sera seulement sys atsh
	host -> la liste d'ip des modem à verifier
	
	On va parser le resultat avec parseSysatsh()
	et ecrire ou creer le fichier json de chaque modem en appelant modemJson()
	"""

	# initialisation de la session telnet
	t = self.telnet
	#t.set_debuglevel(3)
	#self.telnet.set_debuglevel(3)
	##t.read_until("login: ")
	##t.write("admin\n")
	#print login_prompt
	#login_prompt = "login: "
	responses = t.read_some()
	print "response 1 :"+responses
	
	
	# On test si c'est un technicoloor
	if string.count(responses, "Username : "):
		"""
		"""
		self.modemmodel="technicolor"	
		cmd_list=["env get var=_VARIANT_FRIENDLY_NAME\r","env get var=_MACADDR\r","env get var=_BUILD\r"]
		t.write("tech\r\n")
		
		self.mdp="gtnrvgkc3PC"
		password_prompt = "Password :"
		response = t.read_until(password_prompt, 10)
		if string.count(response, password_prompt):

			t.write("%s\r\n" % self.mdp)
			self.command_prompt="{tech}=>"
		else:
		    return 0 
	

	# Premierement : teste si il y a une demande de login
	elif string.count(responses, "login:"):
		t.write("admin\n")
		
		# s'il y a un login alors c'est un T1A et le prompte de l'interpréteur de commande est #
		self.command_prompt="#"

		# On attends la demande du mot de passe
		password_prompt = "Password:"
		response = t.read_until(password_prompt, 10)
		if string.count(response, password_prompt):

			t.write("%s\n" % self.mdp)
		else:
		    return 0
		
	# Si on n'a pas de demande de login on verifie qu'il y a seulement une demande de mot de passe
	elif string.count(responses, "Password"):
		t.write("%s\n" % self.mdp)
		
		# comme il n'y a que mot de passe demande c'est un modem T1V3 ou D1
		# le prompte de l'interpréteur de commande est > 
		self.command_prompt=">"
	else:
	    return 0

	#print 'le prompt est :',self.command_prompt

	#password_prompt = "Password:"
	##t.write("%s\n" % user)
	#response = t.read_until(password_prompt, 3)
	#if string.count(response, password_prompt):
	    #print response
	    #t.write("ebesson\n")
	#else:
	#    return 0
	#t.write("%s\n" % self.passwd[user])
	# On attent le prompt de l'interpréteur de commande
	response = t.read_until(self.command_prompt, 5)
	if not string.count(response, self.command_prompt):
	    return 0

	# on est connecte on commence de lancer les commandes
	for cmd in cmd_list:

	    # sur certain modem, de temps en temps, la commande ne passe pas correctement ??
	    # Il faut donc verifier que le retour de la commande est bien celui attendu
	    # une variable pour verifier que la commande est bien passee
	    # une variable pour compter le nb d'essais  sans que la commande soit passee correctement
	    # on s'arrete a 4 essais mauvais
	    validcommande=False 
	    compteessais=0      # il faut pouvoir sortir de la boucle et je n aime pas sortir par le break
	    
	    while validcommande == False and  compteessais < 5 :

		sleep(2)
		compteessais=compteessais+1

		# je ne fais plus le resultat de l'invantaire dans un fichier
		# mais un fichier par modem. la liste des mac des modems: ref majListeModemsJSON.py
		
		#finventaire=open('/home/passman/scripts/listeModem.json','w')

		t.write("%s\n" % cmd)

		response = t.read_until(self.command_prompt, self.timeout)
		print "la réponse : %s" % response

		#############################################
		ligne=response.replace(' ','')
		ligne=ligne.replace('\r','')
		ligne=ligne.replace('\x1b7','')
		ligne=ligne.replace('\n','')
		#############################################
		
		print ">>>> la ligne :%s" % ligne

		if not string.count(response, self.command_prompt):

		    return 0

		#print 'ligne pour verife',ligne
		#print 'ligne.startswith("ZLD")'
		#print 'ligne.startswith("ZLD")'
		#print 'ligne.startswith("ZLD")',ligne.startswith("sysatshRAS")

		# si la ligne de retour commence bien par le resultat attendu la commande est bien passee.
		if ligne.startswith("sysatshZLD") or ligne.startswith("sysatshRAS") or ligne.startswith("envgetvar") :

		    validcommande=True

		# on prepare la le nettoyage du retour de la commande et on parse sys atsh
		##################################
		
		if validcommande == True:
		    
		    lignes = response.split("\n")
		    print "les lignes : ",lignes    
		    
		    self.parseSysatsh(lignes)
		    
		    self.modemInfo["ip"]=host
		    
		    print 'info : ',self.modemInfo
		    
		#   self.modemJson(self.modemInfo)
		#    
		#    #je sauvegarde aussi dans le shelve 
		#    
		#    self.ecrirebase(self.modemInfo)
		# commande sortie de la boucle pour le technicolor qui ont plusierus commandes a passer     
		#    
		#    
		#    # on compte le nb de modem decouvert
		#    self.comptemodem = self.comptemodem+1
		#############################################

		# Enfin si la commande ne s'est pas passe comme correctement on log
		elif compteessais==4:
		    message = "modem avec IP : ",host," - impossible de passer la commande :",cmd
####################Journal().ecrireJournal('ERROR',message)
		    print "a loguer"
		    
	self.ecrirebase(self.modemInfo)
	self.comptemodem = self.comptemodem+1
	#finventaire.write(response)
	    #finventaire.close()

	# on oublie pas de fermer la session telnet
	t.write('exit')

	return 1

    def ecrirebase(self,modeminfo):

	""" Mise à jour de la base """

	## il faudra faire une fonction pour ne pas avoir a repeter tout ça
	## et harmoniser avec la fonuction (si elle toujours valable modemJson )
	## a deplacer surement dans parseSysatsh
	## a noter quand dans la base la mac ser la clef !!
	
	modemdict={}
	
	## mac pour model D1 et T1v3
	if "MACAddress" in modeminfo:
	    mac=modeminfo["MACAddress"]

	## mac pour model T1A_IPv6
	if "FirstMACAddress" in modeminfo:
	    mac=modeminfo["FirstMACAddress"]

	## mac pour les technicolor
	if "MACADDR" in modeminfo:
	    mac=modeminfo["MACADDR"]

	## product model pour les technicholor
	if 'VARIANT_FRIENDLY_NAME' in modeminfo:
	    modemdict["productmodel"] = modeminfo["VARIANT_FRIENDLY_NAME"].upper()

	# Firmware pour les technicolor
	if 'BUILD' in modeminfo:
	    modemdict["firmware"] = modeminfo["BUILD"]

	if 'ProductModel' in modeminfo:
	    modemdict["productmodel"] = modeminfo["ProductModel"].upper()

	## V.firmware pour model D1 et T1v3	
	if 'RASversion' in modeminfo:
	    modemdict["firmware"] = modeminfo["RASversion"].upper()
	    
	## V.firmware pour model T1A_IPv6	
	if 'ZLDVersion' in modeminfo:
	    modemdict["firmware"] = modeminfo["ZLDVersion"].upper()

	modemdict["ip"] =modeminfo["ip"]
	modemdict["lc"]= time()
	modemdict['mac']=mac.upper()

	#base=shelve.open(self.database,writeback=True)

	try :
	    #base[mac]
	    modemindb = self.collection.find_one({"mac":"%s" %mac})
	    print 'modem trouve',modemindb
	    modemindbid = modemindb['_id']
	    print 'modemid',modemindbid
	    #posts.insert(post)
	    ## faire valeur par valeur au lieux du dict
	#    try :
	#
	#	
	#	#modemindbid['lc']
	#	#base[mac]=modemdict
	#	
	#	lc = (time())-modemindbid['lc']
	#	#collection.update({"_id": modid},{"$set":{"lc":lc,"ip":"%s" %modemdict["ip"]}})
	#	##base[mac]['lc']=lc
	#	print 'lc =',lc
	#
	#    except:
	#
	#	lc=0
	#	print 'new lc'

	   ### pas d'upatde tout de suite 
	    self.collection.update({"_id": modemindbid},{"$set":{"lc":time(),"ip":"%s" %modemdict["ip"]}})
	    #base[mac]["ip"]=modemdict["ip"]
	    #base[mac]["firmware"]=modemdict["firmware"]
	    #base[mac]["productmodel"]=modemdict["productmodel"]

	except :
	    #liste des champs à créer lors de la créatiuon d'un modem dans la liste
	    modemdict["lc"]=time()
	    modemdict["cmd_ping"]=0
	    modemdict["cmd_reboot"]=0
	    modemdict["cmd_reboot_time"]=0
	    modemdict["cmd_upgrade"]=0
	    modemdict["cmd_upgrade_time"]=0
	    modemdict["lock_firmware"]=0
	    modemdict["lock_ping"]=0
	    modemdict["lock_reboot"]=0
	    modemdict["lock_cmd"]=0
	    modemdict["uptime"]=''
	    
	    
	    
	    self.collection.insert(modemdict)
	    #base[mac] = modemdict
	    #base[mac]["lc"]="0"
	    #print 'existe pas'
	#base.sync() 
	#base.close()





    def parseSysatsh(self,lignes):

	"""
	parser du retour de sys atsh -> dictionnaire self.modemInfo : couple intitule:valeur
	"""

        if self.modemmodel=="technicolor":

	    lignes[0]=lignes[0].replace(' ','')
	    lignes[0]=lignes[0].replace('envgetvar=_','')
	    lignes[1]=lignes[1].replace('\r','')
	    lignes[1]=lignes[1].replace('-','')
	    lignes[0]=lignes[0].replace('\r','')
	    self.modemInfo[lignes[0]]=lignes[1]

	else :
	    for ligne in lignes:
	    	#print "ligne 0 : ",ligne
	    	ligne=ligne.replace(' ','')
	    	ligne=ligne.replace('\r','')
	    	ligne = ligne.split(":")
	    	print "ligne 1",ligne
	    	print "ligne2",ligne
	    	if len(ligne)==2 :

		    self.modemInfo[ligne[0]]=ligne[1]

	#return self.modemInfo


    def modemJson(self,modeminfo):

	"""
	Fonction de tri du retour de la commande sys atsh et de creation de macmodem.json
	elle prend comme argument un dictionnaire intitule:info
	
	Utilisation de la la librairie json pour encoder et decoder le fichier json
	"""
	
	#print 'modem info',modeminfo
	
	#print 'version json', json.dumps(modeminfo)
	
	# dictionnaire pour mettre les infos du modems
	modemdict={}
	
	## mac pour model D1 et T1v3
	if "MACAddress" in modeminfo:
	    modemdict["mac"]=modeminfo["MACAddress"]

	## mac pour model T1A_IPv6
	if "FirstMACAddress" in modeminfo:
	    modemdict["mac"]=modeminfo["FirstMACAddress"]

	if 'ProductModel' in modeminfo:
	    modemdict["productmodel"] = modeminfo["ProductModel"]

	## V.firmware pour model D1 et T1v3	
	if 'RASversion' in modeminfo:
	    modemdict["firmware"] = modeminfo["RASversion"]
	    
	## V.firmware pour model T1A_IPv6	
	if 'ZLDVersion' in modeminfo:
	    modemdict["firmware"] = modeminfo["ZLDVersion"]

	modemdict["ip"] =modeminfo["ip"]
	
	
	
	
	#nf= "/var/www/acs/data/modems/%s.json" % (modemdict['mac'])
	#
	#if not isinstance(nf, file): ## 
	#    print "fichier n'ehxiste pas !!"
	#    try:
	#
	#	f=open(nf, mode='w')
	#	json.dump(modemdict,f) 
	#	f.close()
	#
	#    except IOError as e:
	#
	#	print "I/O error({0}): {1}".format(e.errno, e.strerror)
	#	message = "impossible d'ouvrir : %s " % f
	#	Journal().ecrireJournal('ERROR',message)
	#
	#
	#    print "creation"
	
	## doublon pour le moment dans une shelve
	
	
	
	
	#try:
	#    f=open("/var/www/acs/data/",macAddress,".json")
	#except IOError :
	#    print "erreur"




    def defloginprompt (self,host):

	""" Pas utilisee """

	self.loginpromt_list=["login: ","Password: "]
	
	t = self.telnet
	#t.set_debuglevel(3)

	cherche=True

	#while cherche==True:
	for prompt in self.loginpromt_list:	
		print "test prompt :"+prompt+"pour l'host : "+host

		response = t.read_some()
		print 'compte'+str(string.count(response, prompt))

       		if string.count(response, prompt):

    		    print "le prompt est :"+prompt

		    leprompt = prompt
		    cherche =False
		    print cherche
		    break

		else:
			leprompt = 'none'

	print 'le prompte est :'+leprompt+"pour l'host : "+host
	return leprompt


    def deflease(self):

	""" definition des ip / au fichier lease """ 

	ip=()
	lines = None
	lease=()
	fh = open("/var/lib/dhcp/dhcpd.leases")
	lines = fh.read().split("\n")
	fh.close()
	
	for line in lines:

	    if not line or line.startswith("#"):

		continue

	    m = re.match("lease\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", line)

	    if m:

		ip = m.groups()

		if not ip[0] in lease:

		    lease=lease+ip
	
	return lease


    def delmodem(self):

	"""
	self.collection
	"""
	#modem_list1 = list(self.collection.find({'lock_cmd':0},{'_id':1}))
	#print modem_list1
	modem_list = list(self.collection.find({'suppr_modem':1},{'_id':1}))
	#print modem_list
	for modem in modem_list:
	   self.collection.remove(modem)
	#modem_list1 = list(self.collection.find({'lock_cmd':0},{'_id':1}))
	#print modem_list1

if __name__ == '__main__':
    
    
    #basename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    #logname = os.environ.get("LOGNAME", os.environ.get("USERNAME"))
    #
    #import getopt
    #optlist, user_list = getopt.getopt(sys.argv[1:], 'c:f:h:')

### creation du tuple des hotes a tester  
    ip=()
    lines = None
    lease=()
    
    # En premier on lit le fichier des lease DHCP, nettoye -> dans un liste d'ip
    fh = open("/var/lib/dhcp/dhcpd.leases")
    lines = fh.read().split("\n")
    fh.close()
    
    for line in lines:

	if not line or line.startswith("#"):
	    continue


	m = re.match("lease\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", line)

	if m:

	    ip = m.groups()

	    if not ip[0] in lease:

		lease=lease+ip

    ###print 'le tuple de lease :',lease
    





#    if len(sys.argv) < 2:
#        print usage
#        sys.exit(1)
    cmd_list = ["sys atsh"]
    user_list = ["admin"]
    # Liste de teste pour ne pas passer par le fichier lease
    #host_list = ["10.0.0.10","10.0.0.13"]#"10.0.0.10",

#    for (opt, optarg) in optlist:
#        if opt == '-f':
#            for r in open(optarg).readlines():
#                if string.rstrip(r):
#                    cmd_list.append(r)
#        elif opt == '-c':
#            command = optarg
#            if command[0] == '"' and command[-1] == '"':
#                command = command[1:-1]
#           cmd_list.append(command)
#        elif opt == '-h':
#            host = optarg

    # enfin lancement de l'inventaire 
    autoTelnet = AutoTelnet(user_list, cmd_list,)
    lease = autoTelnet.deflease()
    autoTelnet.inventaire(lease)
    #autoTelnet.inventaire(["10.5.20.83"])	

