'''
Filename: bod_config_loader.py
Project: /Users/sofiane/Desktop/APPLICATIONS/code/python-cmpparis-lib/cmpparis
Created Date: Tuesday October 7th 2025
Author: Sofiane (sofiane@klark.app)
-----
Last Modified: Tuesday, 7th October 2025 3:11:48 pm
Modified By: Sofiane (sofiane@klark.app)
-----
Copyright (c) 2025 Klark
'''

"""
Chargeur de configuration BOD

Ce module permet de charger des configurations BOD (Business Object Documents)
à partir de sources variées: dictionnaire Python, fichiers locaux YAML/JSON,
contenu en chaîne et objets stockés sur S3. Il convertit également les noms de
transformateurs en fonctions réelles via le registre de transformateurs.

Examples:
    Charger une configuration depuis un fichier YAML local:

    >>> config = BODConfigLoader.from_yaml("configs/purchase_order.yaml")
    >>> isinstance(config.csv_fieldnames, list)
    True
"""
import json
import yaml
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import logging

from .bod_config import BODConfig
from .bod_transformers import get_transformer

logger = logging.getLogger(__name__)


class BODConfigLoader:
    """Chargeur de configurations BOD depuis différentes sources."""
    
    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> BODConfig:
        """Crée un objet :class:`BODConfig` à partir d'un dictionnaire.

        Cette méthode résout les transformateurs référencés par nom via
        le registre de transformateurs.

        Args:
            config_dict (Dict[str, Any]): Dictionnaire de configuration.

        Returns:
            BODConfig: Instance configurée.

        Raises:
            ValueError: Si un transformateur référencé est introuvable.
        """
        # Extract transformers and convert from names to functions
        header_transformers = None
        line_transformers = None
        
        if 'header_transformers' in config_dict:
            header_transformers = {}
            for field, transformer_name in config_dict['header_transformers'].items():
                header_transformers[field] = get_transformer(transformer_name)
        
        if 'line_transformers' in config_dict:
            line_transformers = {}
            for field, transformer_name in config_dict['line_transformers'].items():
                line_transformers[field] = get_transformer(transformer_name)
        
        return BODConfig(
            header_xpath=config_dict['header_xpath'],
            lines_xpath=config_dict['lines_xpath'],
            header_mapping=config_dict['header_mapping'],
            line_mapping=config_dict['line_mapping'],
            header_transformers=header_transformers,
            line_transformers=line_transformers,
            csv_fieldnames=config_dict.get('csv_fieldnames'),
            flatten_mode=config_dict.get('flatten_mode', 'duplicate_header')
        )
    
    @staticmethod
    def from_yaml(file_path: str) -> BODConfig:
        """Charge une configuration depuis un fichier YAML local.

        Args:
            file_path (str): Chemin du fichier YAML.

        Returns:
            BODConfig: Instance de configuration.
        """
        logger.info(f"Loading BOD config from YAML: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        return BODConfigLoader.from_dict(config_dict)
    
    @staticmethod
    def from_json(file_path: str) -> BODConfig:
        """Charge une configuration depuis un fichier JSON local.

        Args:
            file_path (str): Chemin du fichier JSON.

        Returns:
            BODConfig: Instance de configuration.
        """
        logger.info(f"Loading BOD config from JSON: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        return BODConfigLoader.from_dict(config_dict)
    
    @staticmethod
    def from_s3(bucket: str, key: str, s3_client: Optional[Any] = None) -> BODConfig:
        """Charge une configuration depuis S3.

        Args:
            bucket (str): Nom du bucket S3.
            key (str): Clé de l'objet S3.
            s3_client (Optional[Any]): Client S3 optionnel (utilise ``cmpparis.S3`` si non fourni).

        Returns:
            BODConfig: Instance de configuration.

        Raises:
            ValueError: Si l'extension de fichier n'est pas supportée.
        """
        logger.info(f"Loading BOD config from S3: s3://{bucket}/{key}")
        
        # Use cmpparis S3 class if no client provided
        if s3_client is None:
            from .s3 import S3
            s3_client = S3()
        
        # Download file content
        content = s3_client.download_file_as_string(bucket, key)
        
        # Detect format by extension
        if key.endswith('.yaml') or key.endswith('.yml'):
            config_dict = yaml.safe_load(content)
        elif key.endswith('.json'):
            config_dict = json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {key}. Use .yaml, .yml, or .json")
        
        return BODConfigLoader.from_dict(config_dict)
    
    @staticmethod
    def from_string(content: str, format: str = 'yaml') -> BODConfig:
        """Charge une configuration depuis une chaîne.

        Args:
            content (str): Contenu de la configuration.
            format (str): ``'yaml'`` ou ``'json'``.

        Returns:
            BODConfig: Instance de configuration.

        Raises:
            ValueError: Si le format n'est pas supporté.
        """
        if format.lower() == 'yaml':
            config_dict = yaml.safe_load(content)
        elif format.lower() == 'json':
            config_dict = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'yaml' or 'json'")
        
        return BODConfigLoader.from_dict(config_dict)
    
    @staticmethod
    def validate_config(config_dict: Dict[str, Any]) -> bool:
        """Valide un dictionnaire de configuration.

        Args:
            config_dict (Dict[str, Any]): Configuration à valider.

        Returns:
            bool: ``True`` si la configuration est valide.

        Raises:
            ValueError: Si des champs obligatoires manquent ou si un transformateur est introuvable.
        """
        required_fields = ['header_xpath', 'lines_xpath', 'header_mapping', 'line_mapping']
        
        for field in required_fields:
            if field not in config_dict:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate transformers exist
        if 'header_transformers' in config_dict:
            for transformer_name in config_dict['header_transformers'].values():
                get_transformer(transformer_name)  # Will raise if not found
        
        if 'line_transformers' in config_dict:
            for transformer_name in config_dict['line_transformers'].values():
                get_transformer(transformer_name)  # Will raise if not found
        
        return True