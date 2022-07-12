#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import os
import logging
import csv
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry 
from requests import request
import xml.etree.ElementTree as ET

class UsersCodesStats(object):

    def __init__(self, api_key):
        self.api_key = api_key
        # self.instance = instance
        self.logger = logging.getLogger("__main__.{}".format(__name__))
        # self.logger.debug(instance)              
        self.statut, self.reponse = self.request('GET')
        if self.statut == 'Error' :
            return self.statut, self.reponse
        self.codes_stats = self.reponse.json()
        self.alma_codes_stat_list = self.get_user_stat_categories_in_array()


    @property
    def get_api_key(self,instance="TEST"):
        """Retourne la clef d'api en fonction de l'institution traitée et de l'instance (production ou test de travail)

        Args:
            instance (string): TEST ou PROD 
            institution (string): Code de l'institution UB,UBM, IEP, INP, BXSA

        Returns:
            string: clef d'API
        """
        clef_api = ""
        if instance == 'TEST' :
            clef_api = os.getenv("TEST_NETWORK_API")
        else :
            clef_api = os.getenv("PROD_NETWORK_USER_API")
        self.logger.debug(clef_api)
        return clef_api


    def get_error_message(self,response):
        """Extract error code & error message of an API response
        
        Arguments:
            response {object} -- API REsponse
        
        Returns:
            int -- error code
            str -- error message
        """
        error_code, error_message = '',''
        try :
            content = response.json()
        except : 
            # Parfois l'Api répond avec du xml même si l'en tête demande du Json cas des erreurs de clefs d'API 
            root = ET.fromstring(response.text)
            error_message = root.find(".//xmlb:errorMessage").text if root.find(".//xmlb:errorMessage").text else response.text 
            error_code = root.find(".//xmlb:errorCode").text if root.find(".//xmlb:errorCode").text else '???'
            return error_code, error_message 
        error_message = content['errorList']['error'][0]['errorMessage']
        error_code = content['errorList']['error'][0]['errorCode']
        return error_code, error_message
        
    def request(self,httpmethod, data=None):
        """Envoi un appel à l'api Alma pour injecter les codes des départements et leur libellés

        Args:
            httpmethod (string): Méthode d'appel PUT, GET, POST.
            data (json, optional): . Defaults to None.
        Returns:
            array: status du traitement Success ou Error et Reponse de l'API
        """
        #20190905 retry request 3 time s in case of requests.exceptions.ConnectionError
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.request(
            method=httpmethod,
            headers= {
            "User-Agent" : "pyalma/0.1.0",
            "Authorization" : "clef_api {}".format(self.api_key),
            "Accept" : 'application/json',
            "Content-Type" :'application/json',
        },
            url= "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/code-tables/UserStatCategories?&apikey={}".format(self.api_key),
            data=data)
        try:
            response.raise_for_status()  
        except requests.exceptions.HTTPError:
            print(response.text)
            error_code, error_message= self.get_error_message(response)
            self.logger.error("Alma_Apis :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
            if error_code == '402263' :
                return 'Error_SetExist', "{} -- {}".format(error_code, error_message)
            return 'Error', "{} -- {}".format(error_code, error_message)
        except requests.exceptions.ConnectionError:
            error_code, error_message= self.get_error_message(response)
            self.logger.error("Alma_Apis :: Connection Error: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
            return 'Error', "{} -- {}".format(error_code, error_message)
        except requests.exceptions.RequestException:
            error_code, error_message= self.get_error_message(response)
            self.logger.error("Alma_Apis :: Connection Error: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
            return 'Error', "{} -- {}".format(error_code, error_message)
        return "Success", response

    def get_user_stat_categories_in_array(self) :
        """Liste les codes stats déjà déclarés dans Alma pour la network Zone
        Args:

        return :
        liste : liste contenant la totalité des codes statistiques déclarés dans Alma
        """
        alma_codes_stat_list = []
        for lignes in self.codes_stats['row']:
            alma_codes_stat_list.append(lignes['code'])
        # logger.debug(alma_codes_stat_list)
        return alma_codes_stat_list
        
    def mise_a_jour_codes_stat(self):
        return self.request('PUT',data=json.dumps(self.codes_stats))

    
