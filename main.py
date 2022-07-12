#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import os
import re
import logging

from zipfile import ZipFile
from modules import Codes_Stats_Alma,transferts_ftp,logs
import xml.etree.ElementTree as ET
######################
#PARAMETRES DU SCRIPT#
######################


# Paramètre Alma
DATE_TO_FILES_TO_DL = "20220711" #Date des fichiers lecteurs fourni par la DSI 'AAAAMMJJ'
CLEF_API = os.getenv("PROD_NETWORK_USER_API")
# CLEF_API = os.getenv("TEST_NETWORK_API")

# Logs
APP_NAME = "Alma-Lecteurs-Contrôle-Stat"
LOGS_LEVEL = 'INFO'
LOGS_FILE = "{}/{}".format(os.getenv('LOGS_PATH'),APP_NAME)

# Conf SFTP
HOST = os.getenv("SFTP_UB_HOSTNAME")
USR = os.getenv("SFTP_UB_LOGIN")
PW = os.getenv("SFTP_UB_PW")
REMOTE_FILE_PATH_IN = '/DEPOT/CHARGEUR_LECTEURS'
KNOWN_HOSTS = os.getenv('KNOWN_HOSTS') #Répertoire de stokage des clefs publiques SFTP


#Répertoires de traitement
LOCAL_FILE_PATH_IN = '/tmp/CONTROLE_CODE_STAT_LECTEURS'#Stockage temporaire des fichiers lecteurs
OUT_FILE = '/media/sf_LouxBox/code_a_creer.csv' #Fichier siganlant les codes manquants avec leur catégorie



#On initialise le logger
logs.setup_logging(name=APP_NAME, level=LOGS_LEVEL,log_dir=LOGS_FILE)
logger = logging.getLogger(__name__)


#Création du répertoire de stockage temporaire
if not os.path.exists(LOCAL_FILE_PATH_IN):
    os.mkdir(LOCAL_FILE_PATH_IN)

# Récupération des codes déjà déclarés dans la table UserStatsCategories
users_codes_stats = Codes_Stats_Alma.UsersCodesStats(CLEF_API)
if users_codes_stats.statut == "Error" :
    logger.error("Récupération de la table UserStatCategories :: Impossible de récupérer la table ::{}".format(users_codes_stats.reponse))
    exit()
logger.info("Récupération de la table UserStatsCategories :: OK")

# Récupération des fichiers
statut,file_list = transferts_ftp.load_file(REMOTE_FILE_PATH_IN,LOCAL_FILE_PATH_IN,DATE_TO_FILES_TO_DL,host=HOST, username=USR, password=PW, known_hosts=KNOWN_HOSTS)
if statut == 'Error' :
    exit()

# # Dézipage des fichiers
os.chdir(LOCAL_FILE_PATH_IN)
for item in os.listdir(LOCAL_FILE_PATH_IN): 
        file_name = os.path.abspath(item)
        zip_ref = ZipFile(file_name)
        zip_ref.extractall(LOCAL_FILE_PATH_IN)
        zip_ref.close() # close file
        os.remove(file_name) # delete zipped file

# Traitement des fichiers

report = open(OUT_FILE, "w")
report.write("Institution\tPopulation\tCode stat.\tCatégorie\n")
new_rows = []
unknow_codes_list = []
compteur = 0
for file in os.listdir(LOCAL_FILE_PATH_IN): 
    logger.info(file)
    file_name = re.findall('^.{8}(.*?)_(.*?)\.xml', file)
    institution= file_name[0][0]
    population = file_name[0][1]
    # logger.debug("{} - {}".format(institution,population))
    root = ET.parse(os.path.abspath(file))
    # print(root.tag)
    for stat in root.findall('.//user_statistic'):
        statistic_category = stat.find('./statistic_category').text
        category_type = stat.find('./category_type').text
        if statistic_category not in users_codes_stats.alma_codes_stat_list and statistic_category not in unknow_codes_list :
            new_row = {
                "code": statistic_category,
                "description": "{} - Description à renseigner",
                "default": False,
                "enabled": True,
                "updated_by": "",
                "update_date": ""
            }
            compteur =+ 1
            new_rows.append(new_row)
            unknow_codes_list.append(statistic_category)
            report.write("{}\t{}\t{}\t{}\n".format(institution,population,statistic_category,category_type))
            logger.info("{} :: {} :: {} :: {}".format(institution,population,statistic_category,category_type))
users_codes_stats.codes_stats['row'].extend(new_rows)
logger.info("Traitement terminé. {} codes à ajouter dans la table UserStatsCategories")
report.close
