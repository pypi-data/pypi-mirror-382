"""
Module d'analyse BOD pour la librairie cmpparis

Ce module gère l'analyse (parsing) d'XML BOD (Business Object Documents)
et leur transformation en CSV à plat. Il fournit une classe générique
permettant d'extraire des valeurs via XPath, d'appliquer des transformateurs
et de produire un CSV final.

Examples:
    Analyse d'un BOD et écriture en CSV:

    >>> parser = BODParser()
    >>> csv_text = parser.parse_and_convert(xml_content, config)
    >>> print(csv_text.splitlines()[0])  # affiche l'en-tête CSV
    'col1;col2;col3'
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Callable
import csv
from io import StringIO
from datetime import datetime


class BODParser:
    """Analyseur générique pour documents XML BOD Infor M3.

    Convertit des structures XML hiérarchiques en format CSV à plat selon une
    configuration de mapping.
    """
    
    def __init__(self, namespace: Optional[str] = None):
        """Initialise l'analyseur BOD.

        Args:
            namespace (Optional[str]): Namespace XML. Par défaut, utilise le namespace Infor OAGIS.
        """
        self.namespace = namespace or "http://schema.infor.com/InforOAGIS/2"
        self.ns = {'ns': self.namespace}
        
    def parse_xml_string(self, xml_string: str) -> ET.Element:
        """Analyse une chaîne XML et renvoie l'élément racine.

        Args:
            xml_string (str): Contenu XML sous forme de chaîne.

        Returns:
            xml.etree.ElementTree.Element: Élément racine du document XML.

        Raises:
            xml.etree.ElementTree.ParseError: Si la chaîne n'est pas un XML valide.
        """
        return ET.fromstring(xml_string)
    
    def parse_xml_file(self, file_path: str) -> ET.Element:
        """Analyse un fichier XML et renvoie l'élément racine.

        Args:
            file_path (str): Chemin du fichier XML.

        Returns:
            xml.etree.ElementTree.Element: Élément racine du fichier XML.
        """
        tree = ET.parse(file_path)
        return tree.getroot()
    
    def extract_field(self, element: ET.Element, xpath: str, default: str = "") -> str:
        """Extrait la valeur d'un champ depuis un élément XML via XPath.

        Args:
            element (xml.etree.ElementTree.Element): Élément XML dans lequel chercher.
            xpath (str): Expression XPath.
            default (str): Valeur par défaut si non trouvée.

        Returns:
            str: Valeur trouvée, ou ``default`` si absente.
        """
        try:
            found = element.find(xpath, self.ns)
            if found is not None:
                return found.text or default
            return default
        except Exception:
            return default
    
    def extract_attribute(self, element: ET.Element, xpath: str, attr: str, default: str = "") -> str:
        """Extrait la valeur d'un attribut depuis un élément XML.

        Args:
            element (xml.etree.ElementTree.Element): Élément XML dans lequel chercher.
            xpath (str): XPath pointant vers l'élément.
            attr (str): Nom de l'attribut.
            default (str): Valeur par défaut si non trouvée.

        Returns:
            str: Valeur de l'attribut, ou ``default`` si absente.
        """
        try:
            found = element.find(xpath, self.ns)
            if found is not None:
                return found.get(attr, default)
            return default
        except Exception:
            return default
    
    def extract_multiple(self, element: ET.Element, xpath: str) -> List[ET.Element]:
        """Extrait plusieurs éléments correspondant à un XPath.

        Args:
            element (xml.etree.ElementTree.Element): Élément XML dans lequel chercher.
            xpath (str): Expression XPath.

        Returns:
            List[xml.etree.ElementTree.Element]: Liste des éléments correspondants.
        """
        return element.findall(xpath, self.ns)
    
    def flatten_element(self, element: ET.Element, mapping: Dict[str, Any], 
                       transformers: Optional[Dict[str, Callable]] = None) -> Dict[str, str]:
        """Aplati un élément XML en dictionnaire selon une configuration de mapping.

        Args:
            element (xml.etree.ElementTree.Element): Élément XML à aplatir.
            mapping (Dict[str, Any]): Définition des correspondances champs CSV → XPath.
                - Format simple: ``{"col_csv": "xpath/vers/element"}``
                - Format avancé: ``{"col_csv": {"xpath": "...", "attribute": "..."}}``
            transformers (Optional[Dict[str, Callable]]): Transformateurs optionnels par colonne.
                - Format: ``{"col_csv": lambda x: transform(x)}``

        Returns:
            Dict[str, str]: Dictionnaire aplati.
        """
        result = {}
        transformers = transformers or {}
        
        for csv_col, xml_path in mapping.items():
            # Handle complex mapping with attributes
            if isinstance(xml_path, dict):
                if 'attribute' in xml_path:
                    value = self.extract_attribute(element, xml_path['xpath'], xml_path['attribute'])
                else:
                    value = self.extract_field(element, xml_path['xpath'])
            else:
                # Simple XPath mapping
                value = self.extract_field(element, xml_path)
            
            # Apply transformer if exists
            if csv_col in transformers:
                value = transformers[csv_col](value)
            
            result[csv_col] = value
        
        return result
    
    def parse_header_lines_structure(self, root: ET.Element, 
                                     header_xpath: str,
                                     lines_xpath: str,
                                     header_mapping: Dict[str, Any],
                                     line_mapping: Dict[str, Any],
                                     header_transformers: Optional[Dict[str, Callable]] = None,
                                     line_transformers: Optional[Dict[str, Callable]] = None,
                                     flatten_mode: str = "duplicate_header") -> List[Dict[str, str]]:
        """Analyse une structure XML de type En-tête + Lignes (courant dans les BOD).

        Args:
            root (xml.etree.ElementTree.Element): Élément racine XML.
            header_xpath (str): XPath vers l'élément d'en-tête.
            lines_xpath (str): XPath vers les éléments ligne (relatif à l'en-tête).
            header_mapping (Dict[str, Any]): Mapping des champs d'en-tête.
            line_mapping (Dict[str, Any]): Mapping des champs de ligne.
            header_transformers (Optional[Dict[str, Callable]]): Transformateurs pour l'en-tête.
            line_transformers (Optional[Dict[str, Callable]]): Transformateurs pour les lignes.
            flatten_mode (str): Mode d'aplatissement:
                - ``"duplicate_header"``: chaque ligne reçoit les données d'en-tête.
                - ``"header_only"``: retourner uniquement l'en-tête (ignorer les lignes).
                - ``"lines_only"``: retourner uniquement les lignes (ignorer l'en-tête).

        Returns:
            List[Dict[str, str]]: Liste de dictionnaires aplatis (un par ligne).
        """
        results = []
        
        # Find header
        header_elem = root.find(header_xpath, self.ns)
        if header_elem is None:
            return results
        
        # Extract header data
        header_data = self.flatten_element(header_elem, header_mapping, header_transformers)
        
        if flatten_mode == "header_only":
            return [header_data]
        
        # Find all lines
        lines = self.extract_multiple(header_elem, lines_xpath)
        
        if not lines and flatten_mode == "duplicate_header":
            # No lines but we want header
            return [header_data]
        
        # Process each line
        for line_elem in lines:
            line_data = self.flatten_element(line_elem, line_mapping, line_transformers)
            
            if flatten_mode == "duplicate_header":
                # Merge header + line data
                row = {**header_data, **line_data}
            else:  # lines_only
                row = line_data
            
            results.append(row)
        
        return results
    
    def to_csv(self, data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None) -> str:
        """Convertit une liste de dictionnaires en chaîne CSV.

        Args:
            data (List[Dict[str, str]]): Liste de lignes (dictionnaires).
            fieldnames (Optional[List[str]]): Liste des colonnes (l'ordre compte). Si ``None``, utilise les clés du premier dictionnaire.

        Returns:
            str: Contenu CSV (délimiteur ``;``).
        """
        if not data:
            return ""
        
        fieldnames = fieldnames or list(data[0].keys())
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';', 
                               quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    def parse_and_convert(self, xml_content: str, 
                         config: 'BODConfig',
                         output_csv_path: Optional[str] = None) -> str:
        """Pipeline complète: analyser un BOD XML et convertir en CSV.

        Args:
            xml_content (str): Chaîne XML complète ou chemin vers un fichier XML.
            config (BODConfig): Configuration de mapping BOD.
            output_csv_path (Optional[str]): Chemin optionnel pour écrire le CSV.

        Returns:
            str: Chaîne CSV générée.

        Examples:
            >>> csv_text = BODParser().parse_and_convert(xml_content, config)
            >>> csv_text.startswith('col1;')
            True
        """
        # Parse XML
        if xml_content.startswith('<?xml') or xml_content.startswith('<'):
            root = self.parse_xml_string(xml_content)
        else:
            root = self.parse_xml_file(xml_content)
        
        # Extract data based on config
        data = self.parse_header_lines_structure(
            root=root,
            header_xpath=config.header_xpath,
            lines_xpath=config.lines_xpath,
            header_mapping=config.header_mapping,
            line_mapping=config.line_mapping,
            header_transformers=config.header_transformers,
            line_transformers=config.line_transformers,
            flatten_mode=config.flatten_mode
        )
        
        # Convert to CSV
        csv_output = self.to_csv(data, config.csv_fieldnames)
        
        # Save to file if requested
        if output_csv_path:
            with open(output_csv_path, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_output)
        
        return csv_output