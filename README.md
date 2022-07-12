# Alma Lecteurs Contrôle des codes statitiques

##  Description
Ce script permet d'identifier les codes statistiques usagers non renseignés dans la table **UserStatCategories**.
Pour une date donnée (paramètre DATE_TO_FILES_TO_DL), le programme va télécharger tous les fichiers lecteurs de tous les établissements du réseau fournis par la DSI. Il décompresse chaque fichier et parcour les codes statistiques pour identifier les codes absent de la table **UserStatCategories**. Les codes manquants sont signalés dans un fichier contenant le :
 -  L'institution d'origine : UB, UBM, INP, IEP , BXSA
 - La population concernée : Etudiants, Personnels ou hebergés
 - Le code statistique
 - La description provisoire
 - La catégorie statistique

Le nom est le chemin d'accès au fichier dépendent de la variable **OUT_FILE**

## Utilisation
1. Télécharger ou cloner le contenu de ce répertoire.
2. Installer les modules externes
3. Modifier les paramètres du programme au début du fichier [main.py](main.py) 
4. Exécuter le programme
5. C'est prêt