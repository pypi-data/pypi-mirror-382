####################################################
# utils.py for the 'cmpparis' library
# Created by: Sofiane Charrad
####################################################
"""Utilitaires généraux pour la librairie cmpparis.

Ce module regroupe des fonctions d'aide pour les dates, les chaînes et
quelques validations simples.
"""
from datetime import datetime
import re
import unicodedata

###### Data manipulation ######

# Date functions
def format_date(date, input_format, output_format):
    """Formate une date depuis un format source vers un format cible.

    Args:
        date (str): Chaîne représentant une date.
        input_format (str): Format d'entrée compatible ``datetime.strptime``.
        output_format (str): Format de sortie compatible ``datetime.strftime``.

    Returns:
        str: Date formatée.

    Raises:
        ValueError: Si la date ne correspond pas à ``input_format``.
    """
    return datetime.strptime(date, input_format).strftime(output_format)

def get_current_datetime_formatted(format):
    """Retourne la date/heure actuelle selon un format donné.

    Args:
        format (str): Format de sortie compatible ``datetime.strftime``.

    Returns:
        str: Date/heure courante formatée.
    """
    return datetime.now().strftime(format)

# String functions
def lstrip(value):
    """Supprime les espaces en début de chaîne.

    Args:
        value (str): Chaîne à traiter.

    Returns:
        str: Chaîne sans espaces initiaux.
    """
    return value.lstrip()

def remove_diacritics(value):
    """Supprime les diacritiques (accents) d'une chaîne.

    Args:
        value (str): Chaîne d'entrée.

    Returns:
        str: Chaîne sans diacritiques.
    """
    nfkd_form = unicodedata.normalize('NFKD', value)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def replace(value, pattern, replacement):
    """Remplace les occurrences d'un motif par une valeur.

    Args:
        value (str): Chaîne source.
        pattern (str): Expression régulière.
        replacement (str): Remplacement.

    Returns:
        str: Chaîne modifiée.
    """
    return re.sub(pattern, replacement, value)

def replace_ampersand(value):
    """Remplace ``&`` par ``+``.

    Args:
        value (str): Chaîne source.

    Returns:
        str: Chaîne avec remplacement.
    """
    return value.replace('&', '+')

def replace_comma(value):
    """Remplace les virgules par des points.

    Args:
        value (str): Chaîne numérique.

    Returns:
        str: Chaîne avec virgules remplacées.
    """
    return value.replace(',', '.')

def replace_endash(value):
    """Remplace le demi-cadratin (–) par un tiret (-)."""
    return value.replace('–', '-')

def replace_emdash(value):
    """Remplace le cadratin (—) par un tiret (-)."""
    return value.replace('—', '-')

def rstrip(value):
    """Supprime les espaces en fin de chaîne."""
    return value.rstrip()

def tofloat(value):
    """Convertit une chaîne en float.

    Args:
        value (str | int | float): Valeur à convertir.

    Returns:
        float: Valeur convertie.

    Raises:
        ValueError: Si la valeur ne peut pas être convertie.
        TypeError: Si le type est incompatible.
    """
    return float(value)

def toint(value):
    """Convertit une chaîne en int.

    Args:
        value (str | int | float): Valeur à convertir.

    Returns:
        int: Valeur convertie.

    Raises:
        ValueError: Si la valeur ne peut pas être convertie.
        TypeError: Si le type est incompatible.
    """
    return int(value)

def upper(value):
    """Met en majuscules.

    Args:
        value (str): Chaîne source.

    Returns:
        str: Chaîne en majuscules.
    """
    return value.upper()

###### Data checking ######

def check_email(value):
    """Vérifie si une chaîne est une adresse email valide (regex simple).

    Args:
        value (str): Adresse email.

    Returns:
        bool: ``True`` si correspond au motif, sinon ``False``.
    """
    return False if re.fullmatch(r"^[\w\-\.]+@([\w\-]+\.)+[\w]{2,4}$", value) == None else True

def check_empty_value(value):
    """Teste si une valeur est non vide et non ``None``.

    Args:
        value (Any): Valeur à tester.

    Returns:
        bool: ``True`` si non vide et non ``None``.
    """
    return False if len(value) == 0 or value == None else True

def check_encoding(value):
    """Vérifie si une chaîne peut être encodée en ASCII (via UTF-8 -> ASCII).

    Args:
        value (str): Chaîne à tester.

    Returns:
        bool: ``True`` si convertible en ASCII, sinon ``False``.
    """
    try:
        value.encode('utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True