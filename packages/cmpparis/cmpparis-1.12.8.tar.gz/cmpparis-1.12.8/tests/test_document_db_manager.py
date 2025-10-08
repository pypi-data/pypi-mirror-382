import pytest
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from cmpparis.document_db_manager import DocumentDBManager

@pytest.fixture
def mock_mongo_client():
    with patch('cmpparis.document_db_manager.pymongo.MongoClient') as mock_client:
        yield mock_client

@pytest.fixture
def db_manager(mock_mongo_client):
    # Instancie DocumentDBManager avec des valeurs fictives
    return DocumentDBManager(
        db_user="test_user",
        db_pwd="test_pwd",
        db_host="test_host",
        database_name="test_db",
        collection_name="test_collection",
        pem_file_path="test.pem"
    )

def test_connect_to_documentdb(mock_mongo_client, db_manager):
    # Récupérer le chemin complet du fichier PEM tel qu'il est utilisé dans le code
    expected_pem_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../cmpparis/global-bundle.pem'))

    # Construire la chaîne de connexion attendue
    expected_uri = (
        f"mongodb://test_user:test_pwd@test_host:27017/"
        f"?tls=true&tlsCAFile={expected_pem_path}&retryWrites=false&directConnection=true"
    )

    # Vérifie que la méthode de connexion est appelée correctement
    mock_mongo_client.assert_called_once_with(expected_uri)

def test_insert_document(db_manager):
    mock_insert = db_manager.collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="test_id"))
    
    data = {"key": "value"}
    data['createdAt'] = datetime.now()
    data['lastModificationAt'] = datetime.now()
    result = db_manager.insert_document(data)
    
    mock_insert.assert_called_once_with(data)
    assert result == "test_id"

def test_update_document(db_manager):
    mock_update = db_manager.collection.update_one = MagicMock(return_value=MagicMock(modified_count=1))
    
    # Appel de la méthode
    result = db_manager.update_document({"key": "value"}, {"key": "new_value"})
    
    # Vérification de l'appel
    mock_update.assert_called_once_with({"key": "value"}, {"$set": {"key": "new_value"}})
    
    # Vérification du résultat
    assert result == 1

def test_get_document(db_manager):
    mock_find = db_manager.collection.find_one = MagicMock(return_value={"key": "value"})
    
    result = db_manager.get_document("key", "value")
    
    mock_find.assert_called_once_with({"key": "value"})
    assert result == {"key": "value"}

def test_get_documents(db_manager):
    mock_find = db_manager.collection.find = MagicMock(return_value=[{"key": "value"}])
    
    result = list(db_manager.get_documents(projection={"key": 1}, filter={"key": "value"}))
    
    mock_find.assert_called_once_with(filter={"key": "value"}, projection={"key": 1})
    assert result == [{"key": "value"}]

def test_update_list_in_document(db_manager):
    mock_update = db_manager.collection.update_one = MagicMock()
    
    db_manager.update_list_in_document({"key": "value"}, "list_field", "new_item")
    
    mock_update.assert_called_once_with({"key": "value"}, {"$push": {"list_field": "new_item"}})

def test_delete_document(db_manager):
    mock_delete = db_manager.collection.delete_one = MagicMock()
    
    db_manager.delete_document("test_id")
    
    mock_delete.assert_called_once_with({"_id": "test_id"})

def test_delete_all_documents(db_manager):
    mock_delete_many = db_manager.collection.delete_many = MagicMock()
    
    db_manager.delete_all_documents()
    
    mock_delete_many.assert_called_once_with({})
