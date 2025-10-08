####################################################
# document_db_manager.py for the 'cmpparis' library
# Created by: Sofiane Charrad
####################################################
"""Gestionnaire simplifié pour AWS DocumentDB/MongoDB.

Ce module fournit une classe utilitaire ``DocumentDBManager`` pour se connecter
à une base DocumentDB/MongoDB et effectuer des opérations CRUD courantes.
"""

import os
import pymongo
import sys
import urllib

from bson import ObjectId
from datetime import datetime

class DocumentDBManager:
    """Gestionnaire d'accès pour DocumentDB/MongoDB."""

    def __init__(self, db_user="root", db_pwd="", db_host="localhost", database_name="my_database", collection_name="my_collection", pem_file_path=None):
        """Initialise la connexion et sélectionne la base/collection.

        Args:
            db_user (str): Utilisateur de la base.
            db_pwd (str): Mot de passe.
            db_host (str): Hôte DocumentDB/MongoDB.
            database_name (str): Nom de la base de données.
            collection_name (str): Nom de la collection.
            pem_file_path (str | None): Chemin vers le certificat CA.
        """
        self.db_user = db_user
        self.db_pwd = db_pwd
        self.db_host = db_host
        self.database_name = database_name
        self.collection_name = collection_name
        self.pem_file_path = pem_file_path or '/opt/python/utils/global-bundle.pem'
        
        if not os.path.exists(self.pem_file_path):
            self.pem_file_path = os.path.join(os.path.dirname(__file__), 'global-bundle.pem')
        
        self.client = self.connect_to_documentdb()
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]

    def connect_to_documentdb(self):
        """Établit la connexion MongoDB/DocumentDB et retourne le client.

        Returns:
            pymongo.MongoClient: Client connecté.

        Raises:
            SystemExit: En cas d'erreur de connexion.
        """
        try:
            client = pymongo.MongoClient(
                f"mongodb://{self.db_user}:{self.db_pwd}@{self.db_host}:27017/?tls=true&tlsCAFile={self.pem_file_path}&retryWrites=false&directConnection=true")
            print("Client ok :", client)
            return client
        except Exception as e:
            print("Error while connecting to DocumentDB : ", e)
            sys.exit(1)

    def insert_document(self, document):
        """Insère un document et renvoie son identifiant.

        Args:
            document (dict): Document à insérer.

        Returns:
            ObjectId | None: Identifiant inséré, ``None`` en cas d'erreur.
        """
        try:
            document['createdAt'] = datetime.now()
            document['lastModificationAt'] = datetime.now()

            result = self.collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            print(f"Error while inserting data into documentDB : {e}")

    def update_document(self, filter_criteria, update_data):
        """Met à jour un document correspondant à un filtre.

        Args:
            filter_criteria (dict): Filtre de sélection.
            update_data (dict): Données à appliquer avec ``$set``.

        Returns:
            int | None: Nombre de documents modifiés, ``None`` en cas d'erreur.
        """
        try:
            result = self.collection.update_one(filter_criteria, {'$set': update_data})
            return result.modified_count
        except Exception as e:
            print(f"Error while updating data in documentDB : {e}")

    def get_document(self, column, value):
        """Récupère un document par valeur d'une colonne.

        Args:
            column (str): Nom du champ.
            value (Any): Valeur recherchée.

        Returns:
            dict | None: Document trouvé ou ``None``.
        """
        try:
            return self.collection.find_one({column: value})
        except Exception as e:
            print(f"Error while getting data from documentDB : {e}")

    def get_documents(self, projection=None, filter=None):
        """Récupère un curseur de documents selon un filtre et une projection.

        Args:
            projection (dict | None): Projection des champs.
            filter (dict | None): Filtre de sélection.

        Returns:
            pymongo.cursor.Cursor | None: Curseur de résultats, ``None`` en cas d'erreur.
        """
        try:
            return self.collection.find(filter=filter, projection=projection)
        except Exception as e:
            print(f"Error while getting data from documentDB : {e}")

    def update_list_in_document(self, filter, list_name, list_value):
        """Ajoute un élément à une liste dans un document.

        Args:
            filter (dict): Filtre pour trouver le document.
            list_name (str): Nom du champ liste.
            list_value (Any): Valeur à pousser dans la liste.
        """
        try:
            self.collection.update_one(filter, {"$push": {list_name: list_value}})
        except Exception as e:
            print(f"Error while updating list in documentDB : {e}")

    def delete_document(self, id):
        """Supprime un document par identifiant.

        Args:
            id (ObjectId): Identifiant du document.
        """
        try:
            self.collection.delete_one({"_id": id})
            print("Document successfully deleted")
        except Exception as e:
            print(f"Error while deleting data from documentDB : {e}")

    def delete_all_documents(self):
        """Supprime tous les documents de la collection courante."""
        try:
            self.collection.delete_many({})
            print("All documents are successfully deleted")
        except Exception as e:
            print(f"Error while deleting data from documentDB : {e}")