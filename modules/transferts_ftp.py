#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import os
import logging
import pysftp

#Init logger
logger = logging.getLogger("__main__.{}".format(__name__))
# cnopts = pysftp.CnOpts()
# cnopts.hostkeys = None

# Récupération des fichiers
def load_file(remote_file_path_in,local_file_path_in,file_prefix,host=os.getenv("SFTP_UB_HOSTNAME"), username=os.getenv("SFTP_UB_LOGIN"), password=os.getenv("SFTP_UB_PW"), known_hosts = os.getenv('KNOWN_HOSTS')):
    cnopts = pysftp.CnOpts(knownhosts=known_hosts)
    try :
        # Connexion au serveur
        with pysftp.Connection(host=host, username=username, password=password,cnopts=cnopts,log=True) as sftp:
            logger.info("Récupération des fichiers::Connexion au serveur ftp ok")
            file_list = []
            sftp.chdir(remote_file_path_in)
            for file in sftp.listdir_attr():
                file_name = file.filename
                if file_name[:8] == file_prefix :
                    try : 
            #           # Transfert des fichiers
                        sftp.get(file_name, "{}/{}".format(local_file_path_in,file_name), preserve_mtime=True)
                        file_list.append(file_list)
                    except Exception as e:
                        logger.error("Récupération des fichiers::Impossible de transférer les fichiers {} ::{}".format(file_name,str(e)))
            return "Success", file_list 
    except Exception as e:
        logger.error("Récupération des fichiers::Impossible de se connecter au serveur ftp::{}".format(str(e)))
        return "Error", str(e)

