from bottle import *
import os
import re
import rsa
import base64
from subprocess import Popen, PIPE

from pgoweb import player

from pgoapi import pgoapi

#=============VARIABLES=============================================

# Definition des variables globales
Debug = False

#Chargement de la cle privee
with open(os.path.dirname(os.path.realpath(__file__))+'/id_rsa') as privatefile:
    keydata = privatefile.read()
Privkey = rsa.PrivateKey.load_pkcs1(keydata)

#=============METHODES=============================================

#Affiche l'erreur
def showError(data, message):
    data["state"] = "NO"
    data["message"] = message
    return data


#Retourne les informations de l'utilisateur precise
@route("/api", method=['GET', 'POST'])
def api():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    #Creation du dictionnaire de donnees
    data = {"state" : "OK", "message" : ""};
    if Debug == False:
        #Determination des arguments (decryptage)
        params = request.query.get("params")
        if params == None: #Si c'est pas en get, on recupere en POST
            params = request.forms.get("params")
        params = params + "=="
        params = base64.urlsafe_b64decode(params)

        params = rsa.decrypt(params, Privkey)
        params = params.split("&")
        userparam = params[0]
        #Suppression du premier arguments
        params.remove(userparam)
        #Join de toutes les arguments restants en mot de passe (contourner probleme si mdp contient un &)
        passwordparam = "".join(params)
    else:
        userparam = request.query.get("user")
        passwordparam = request.query.get("password")
    
    #verification des parametres
    if userparam == None or passwordparam == None:
        return showError(data, "You must specify a username and a password")


    #Systeme d'authentification
    auth_method = 'ptc'
    if "@gmail.com" in userparam:
        auth_method = 'google'

    #Lancement de l'api
    api = pgoapi.PGoApi()
    if not api.login(auth_method, userparam, passwordparam):
        return showError(data, "Wrong username/password or server error")

    #Récupération des informations
    api.get_player() #sur le joueur
    api.get_inventory() #son inventaire
    api_data = api.call()


    pl = player.Player(api_data["responses"]["GET_PLAYER"])
    pl.setPlayerStats(api_data["responses"]["GET_INVENTORY"])
    pl.setTeam(api_data["responses"]["GET_INVENTORY"])

    data["player"] = pl.getDataAsJson()
    return data


#Retourne la clef publique 
@route("/pubkey")
def getpubkey():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    #Chargement de la cle privee
    with open(os.path.dirname(os.path.realpath(__file__))+'/id_rsa.pub') as privatefile:
        keydata = privatefile.read()
    return {"pubkey" : keydata}


if Debug == False: 
    application = default_app()
else:
    run(host='localhost', port=8080)