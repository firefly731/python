#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os

def verif_MAC(mac, sep=""):
    m = re.findall(r"[0-9A-F]", mac.upper())
    if re.search(r"[^0-9A-F-:\s.\ufeff]", mac.upper()) is None and len(m) == 12:
        m = "".join(m)
        return re.sub(r"(?P<MAC1>\w{2})(?P<MAC2>\w{2})(?P<MAC3>\w{2})(?P<MAC4>\w{2})(?P<MAC5>\w{2})(?P<MAC6>\w{2})", r"\g<MAC1>{0}\g<MAC2>{0}\g<MAC3>{0}\g<MAC4>{0}\g<MAC5>{0}\g<MAC6>".format(sep), m)


def read_file(chemin):
    if re.search(r'^(\'|\").*(\'|\")$', chemin.strip()):
        chemin = re.sub(r'^(\'|\")(?P<chem>.*)(\'|\")$', r'\g<chem>', chemin.strip())
    if re.search(r'(.txt)$', chemin) is not None:
        try:
            liste = []
            with open(chemin, 'r', encoding='utf-8') as f:
                for l in f:
                    liste.append(l.strip())
                return chemin, liste
        except PermissionError:
            print("Problème de droits en lecture")
        except FileNotFoundError:
            print("Fichier introuvable")
    else:
        print('Format de fichier incorrect !!!')

def write_file(chemin, liste, sep):
    success = False
    erreur = False
    try:
        with open(chemin, 'w', encoding='utf-8') as f:
            success = True
            for l in liste:
                if verif_MAC(l, sep) is not None:
                    f.write("{}\n".format(verif_MAC(l, sep)))
                else:
                    f.write("{} !!!Adresse MAC non valide!!!\n".format(l))
                    erreur = True
            return erreur, success
    except PermissionError:
        print("Problème de droits en écriture")
    return erreur, success


print("\n!!! Conversion adresse MAC !!!\n")
chemin_file = input("Veuillez saisir une adresse MAC, ou l'emplacement d'un fichier au format .txt: ")

liste_sep = ["-",":","espace","aucun"]
for i,sep in enumerate(liste_sep):
    print("{0}   :   séparateur {1}\n".format(i,sep))
liste_sep = ["-",":"," ",""]
separateur = input("Veuillez choisir le numéro correspondant au séparateur voulu : ")
while re.search(r'^[0-3]', separateur) is None:
    separateur = input("Veuillez saisir un numéro valide : ")

if verif_MAC(chemin_file) is not None:
    print(verif_MAC(chemin_file, liste_sep[int(separateur)]))
else:
    if read_file(chemin_file) is not None:
        chemin, liste = read_file(chemin_file)
        file_name = (os.path.basename(chemin)).split(".")[0]
        chemin_file_modif = re.sub(file_name, '{}-new'.format(file_name), chemin)
        erreur, success = write_file(chemin_file_modif, liste, liste_sep[int(separateur)])
        if erreur == False and success == True:
            print("Fichier {}-new a été crée correctement".format(file_name))
        elif erreur == True and success == True:
            print("Fichier {}-new a été crée correctement".format(file_name))
            print("Certaines adresses MAC contiennent des erreurs !!!")
os.system("PAUSE")  



