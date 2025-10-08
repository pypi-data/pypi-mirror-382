"""
Registre de transformateurs BOD

Ce module fournit un ensemble de fonctions de transformation prêtes à l'emploi
pour normaliser, formater et nettoyer des valeurs de champs BOD (Business Object
Document). Il inclut également un registre permettant de récupérer, lister,
enchaîner et enregistrer des transformateurs personnalisés.

Examples:
    Récupérer et appliquer un transformateur existant:

    >>> transformer = get_transformer("uppercase")
    >>> transformer("bonjour")
    'BONJOUR'

    Enchaîner plusieurs transformateurs:

    >>> chained = chain_transformers("strip_whitespace", "uppercase", "truncate")
    >>> chained("  hello world  ")
    'HELLO WORL'
"""
from datetime import datetime
from typing import Callable, Dict, Optional
import re


def date_format(value: str) -> str:
    """Extrait la date d'un datetime ISO (supprime la partie heure).

    Args:
        value (str): Chaîne au format ISO 8601 (ex: "2025-09-09T00:00:00.000Z").

    Returns:
        str: La date au format ``YYYY-MM-DD``. Retourne une chaîne vide si ``value`` est vide.

    Examples:
        >>> date_format("2025-09-09T00:00:00.000Z")
        '2025-09-09'
        >>> date_format("2025-09-09")
        '2025-09-09'
    """
    if not value:
        return ""
    return value.split('T')[0] if 'T' in value else value


def datetime_format(value: str) -> str:
    """Formate un datetime ISO en ``YYYY-MM-DD HH:MM:SS``.

    Args:
        value (str): Chaîne datetime au format ISO 8601.

    Returns:
        str: Datetime formaté ``YYYY-MM-DD HH:MM:SS``. Retourne la valeur d'origine si parsing impossible, ou une chaîne vide si ``value`` est vide.

    Examples:
        >>> datetime_format("2025-09-09T09:33:09.770Z")
        '2025-09-09 09:33:09'
    """
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return value


def datetime_to_date(value: str) -> str:
    """Convertit un datetime en date uniquement.

    Alias de :func:`date_format`.

    Args:
        value (str): Chaîne datetime au format ISO 8601.

    Returns:
        str: La date au format ``YYYY-MM-DD``.
    """
    return date_format(value)


def uppercase(value: str) -> str:
    """Convertit en majuscules.

    Args:
        value (str): Chaîne à convertir.

    Returns:
        str: Chaîne en majuscules, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> uppercase("hello")
        'HELLO'
    """
    return value.upper() if value else ""


def lowercase(value: str) -> str:
    """Convertit en minuscules.

    Args:
        value (str): Chaîne à convertir.

    Returns:
        str: Chaîne en minuscules, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> lowercase("HELLO")
        'hello'
    """
    return value.lower() if value else ""


def strip_whitespace(value: str) -> str:
    """Supprime les espaces de début et de fin.

    Args:
        value (str): Chaîne à nettoyer.

    Returns:
        str: Chaîne sans espaces superflus aux extrémités, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> strip_whitespace("  hello  ")
        'hello'
    """
    return value.strip() if value else ""


def boolean_to_yes_no(value: str) -> str:
    """Convertit une chaîne booléenne en ``Yes``/``No``.

    Sont considérées comme vraies: ``"true"``, ``"1"``, ``"yes"`` (insensible à la casse).

    Args:
        value (str): Chaîne représentant un booléen.

    Returns:
        str: ``"Yes"`` si vrai, ``"No"`` sinon. Chaîne vide si ``value`` est vide.

    Examples:
        >>> boolean_to_yes_no("true")
        'Yes'
        >>> boolean_to_yes_no("false")
        'No'
    """
    if not value:
        return ""
    return "Yes" if value.lower() in ['true', '1', 'yes'] else "No"


def boolean_to_01(value: str) -> str:
    """Convertit une chaîne booléenne en ``0``/``1``.

    Args:
        value (str): Chaîne représentant un booléen.

    Returns:
        str: ``"1"`` si vrai, ``"0"`` sinon. Retourne ``"0"`` si ``value`` est vide.

    Examples:
        >>> boolean_to_01("true")
        '1'
        >>> boolean_to_01("false")
        '0'
    """
    if not value:
        return "0"
    return "1" if value.lower() in ['true', '1', 'yes'] else "0"


def float_format_2(value: str) -> str:
    """Formate un nombre avec 2 décimales.

    Args:
        value (str): Chaîne numérique.

    Returns:
        str: Nombre formaté avec 2 décimales. Retourne la valeur d'origine si parsing impossible, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> float_format_2("123.456")
        '123.46'
    """
    if not value:
        return ""
    try:
        return f"{float(value):.2f}"
    except:
        return value


def float_format_3(value: str) -> str:
    """Formate un nombre avec 3 décimales.

    Args:
        value (str): Chaîne numérique.

    Returns:
        str: Nombre formaté avec 3 décimales. Retourne la valeur d'origine si parsing impossible, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> float_format_3("123.4567")
        '123.457'
    """
    if not value:
        return ""
    try:
        return f"{float(value):.3f}"
    except:
        return value


def integer_format(value: str) -> str:
    """Convertit en entier (supprime les décimales).

    Args:
        value (str): Chaîne numérique.

    Returns:
        str: Entier sous forme de chaîne. Retourne la valeur d'origine si parsing impossible, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> integer_format("123.456")
        '123'
    """
    if not value:
        return ""
    try:
        return str(int(float(value)))
    except:
        return value


def remove_currency_symbol(value: str) -> str:
    """Supprime les symboles monétaires courants d'une chaîne.

    Args:
        value (str): Chaîne contenant un montant.

    Returns:
        str: Chaîne sans symboles monétaires.

    Examples:
        >>> remove_currency_symbol("$123.45")
        '123.45'
    """
    if not value:
        return ""
    for symbol in ['$', '€', '£', '¥', '₹', 'USD', 'EUR', 'GBP']:
        value = value.replace(symbol, '')
    return value.strip()


def remove_special_chars(value: str) -> str:
    """Supprime les caractères spéciaux, conserve uniquement alphanumériques et espaces.

    Args:
        value (str): Chaîne à nettoyer.

    Returns:
        str: Chaîne ne contenant que des lettres, chiffres et espaces.

    Examples:
        >>> remove_special_chars("Hello@World!")
        'HelloWorld'
    """
    if not value:
        return ""
    return re.sub(r'[^a-zA-Z0-9\s]', '', value)


def replace_comma_with_dot(value: str) -> str:
    """Remplace la virgule par un point (nombres décimaux).

    Args:
        value (str): Chaîne numérique utilisant la virgule.

    Returns:
        str: Chaîne avec les virgules remplacées par des points.

    Examples:
        >>> replace_comma_with_dot("123,45")
        '123.45'
    """
    if not value:
        return ""
    return value.replace(',', '.')


def replace_dot_with_comma(value: str) -> str:
    """Remplace le point par une virgule (format européen).

    Args:
        value (str): Chaîne numérique utilisant le point.

    Returns:
        str: Chaîne avec les points remplacés par des virgules.

    Examples:
        >>> replace_dot_with_comma("123.45")
        '123,45'
    """
    if not value:
        return ""
    return value.replace('.', ',')


def truncate(value: str, max_length: int = 50) -> str:
    """Tronque une chaîne à une longueur maximale.

    Args:
        value (str): Chaîne à tronquer.
        max_length (int): Longueur maximale souhaitée. Par défaut 50.

    Returns:
        str: Chaîne tronquée à ``max_length`` caractères, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> truncate("Hello World", 5)
        'Hello'
    """
    if not value:
        return ""
    return value[:max_length]


def pad_left(value: str, length: int = 10, char: str = '0') -> str:
    """Complète une chaîne à gauche avec un caractère.

    Args:
        value (str): Chaîne à compléter.
        length (int): Longueur totale souhaitée. Par défaut 10.
        char (str): Caractère de remplissage. Par défaut '0'.

    Returns:
        str: Chaîne complétée à gauche.

    Examples:
        >>> pad_left("123", 6, "0")
        '000123'
    """
    if not value:
        return char * length
    return value.rjust(length, char)


def pad_right(value: str, length: int = 10, char: str = ' ') -> str:
    """Complète une chaîne à droite avec un caractère.

    Args:
        value (str): Chaîne à compléter.
        length (int): Longueur totale souhaitée. Par défaut 10.
        char (str): Caractère de remplissage. Par défaut ' '.

    Returns:
        str: Chaîne complétée à droite.

    Examples:
        >>> pad_right("ABC", 5)
        'ABC  '
    """
    if not value:
        return char * length
    return value.ljust(length, char)


def clean_text(value: str) -> str:
    """Nettoie un texte: trim, espaces multiples, caractères spéciaux problématiques.

    - Remplace les espaces multiples par un seul espace.
    - Supprime les retours à la ligne, tabulations.
    - Supprime les espaces en début et fin.

    Args:
        value (str): Chaîne à nettoyer.

    Returns:
        str: Chaîne nettoyée, ou chaîne vide si ``value`` est vide.

    Examples:
        >>> clean_text("  Hello    World!  ")
        'Hello World'
    """
    if not value:
        return ""
    # Remove extra spaces
    value = re.sub(r'\s+', ' ', value)
    # Strip
    value = value.strip()
    # Remove common problematic chars but keep basic punctuation
    value = value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    return value


def default_if_empty(value: str, default: str = "N/A") -> str:
    """Retourne une valeur par défaut si la chaîne est vide.

    Args:
        value (str): Chaîne initiale.
        default (str): Valeur par défaut à utiliser. Par défaut "N/A".

    Returns:
        str: ``value`` si non vide, sinon ``default``.

    Examples:
        >>> default_if_empty("", "Unknown")
        'Unknown'
    """
    return value if value else default


def extract_digits(value: str) -> str:
    """Extrait uniquement les chiffres d'une chaîne.

    Args:
        value (str): Chaîne source.

    Returns:
        str: Chaîne composée uniquement de chiffres.

    Examples:
        >>> extract_digits("ABC123XYZ456")
        '123456'
    """
    if not value:
        return ""
    return ''.join(filter(str.isdigit, value))


def extract_letters(value: str) -> str:
    """Extrait uniquement les lettres d'une chaîne.

    Args:
        value (str): Chaîne source.

    Returns:
        str: Chaîne composée uniquement de lettres.

    Examples:
        >>> extract_letters("ABC123XYZ456")
        'ABCXYZ'
    """
    if not value:
        return ""
    return ''.join(filter(str.isalpha, value))


def first_word(value: str) -> str:
    """Extrait le premier mot d'une chaîne.

    Args:
        value (str): Chaîne source.

    Returns:
        str: Premier mot, ou chaîne vide si aucun.

    Examples:
        >>> first_word("Hello World Test")
        'Hello'
    """
    if not value:
        return ""
    return value.split()[0] if value.split() else ""


def last_word(value: str) -> str:
    """Extrait le dernier mot d'une chaîne.

    Args:
        value (str): Chaîne source.

    Returns:
        str: Dernier mot, ou chaîne vide si aucun.

    Examples:
        >>> last_word("Hello World Test")
        'Test'
    """
    if not value:
        return ""
    return value.split()[-1] if value.split() else ""


def prefix(value: str, prefix_str: str = "") -> str:
    """Ajoute un préfixe à une chaîne.

    Args:
        value (str): Chaîne source.
        prefix_str (str): Préfixe à ajouter.

    Returns:
        str: Chaîne préfixée. Retourne ``prefix_str`` si ``value`` est vide.

    Examples:
        >>> prefix("123", "ID_")
        'ID_123'
    """
    if not value:
        return prefix_str
    return f"{prefix_str}{value}"


def suffix(value: str, suffix_str: str = "") -> str:
    """Ajoute un suffixe à une chaîne.

    Args:
        value (str): Chaîne source.
        suffix_str (str): Suffixe à ajouter.

    Returns:
        str: Chaîne suffixée. Retourne ``suffix_str`` si ``value`` est vide.

    Examples:
        >>> suffix("file", ".csv")
        'file.csv'
    """
    if not value:
        return suffix_str
    return f"{value}{suffix_str}"


def normalize_phone(value: str) -> str:
    """Normalise un numéro de téléphone (garde uniquement ``+`` et chiffres).

    Args:
        value (str): Numéro de téléphone brut.

    Returns:
        str: Numéro normalisé.

    Examples:
        >>> normalize_phone("+33 (0)1 23 45 67 89")
        '+33123456789'
    """
    if not value:
        return ""
    # Keep + and digits only
    return re.sub(r'[^\d+]', '', value)


def format_ean13(value: str) -> str:
    """Formate un code-barres EAN-13 (13 chiffres, complété avec des zéros).

    Args:
        value (str): Chaîne contenant des chiffres.

    Returns:
        str: Chaîne de 13 chiffres (zéro-remplie et tronquée si nécessaire). Retourne une chaîne vide si ``value`` est vide.

    Examples:
        >>> format_ean13("123456")
        '0000000123456'
    """
    if not value:
        return ""
    digits = extract_digits(value)
    return digits.zfill(13)[:13]  # Pad to 13 digits and truncate if longer


def null_to_empty(value: str) -> str:
    """Convertit ``NULL``, ``None``, ``null``, ``N/A`` ou ``NA`` en chaîne vide.

    Args:
        value (str): Chaîne à normaliser.

    Returns:
        str: Chaîne vide si valeur nulle/indisponible, sinon ``value``.
    """
    if not value or value.lower() in ['null', 'none', 'n/a', 'na']:
        return ""
    return value


def empty_to_zero(value: str) -> str:
    """Convertit une chaîne vide en ``0`` (utile pour les champs numériques).

    Args:
        value (str): Chaîne à convertir.

    Returns:
        str: ``"0"`` si vide, sinon ``value``.
    """
    if not value or value.strip() == "":
        return "0"
    return value


def yes_no_to_boolean(value: str) -> str:
    """Convertit ``Yes/No`` (ou ``Oui/Non``) en ``true/false``.

    Args:
        value (str): Chaîne représentant Oui/Non.

    Returns:
        str: ``"true"`` pour Oui/Yes, ``"false"`` sinon. ``"false"`` si ``value`` est vide.

    Examples:
        >>> yes_no_to_boolean("Yes")
        'true'
        >>> yes_no_to_boolean("No")
        'false'
    """
    if not value:
        return "false"
    return "true" if value.lower() in ['yes', 'oui', 'y', 'o'] else "false"


# Registry of all available transformers
TRANSFORMER_REGISTRY: Dict[str, Callable] = {
    # Date/Time transformers
    "date_format": date_format,
    "datetime_format": datetime_format,
    "datetime_to_date": datetime_to_date,
    
    # Text transformers
    "uppercase": uppercase,
    "lowercase": lowercase,
    "strip_whitespace": strip_whitespace,
    "clean_text": clean_text,
    "truncate": truncate,
    "remove_special_chars": remove_special_chars,
    
    # Number transformers
    "float_format_2": float_format_2,
    "float_format_3": float_format_3,
    "integer_format": integer_format,
    "remove_currency_symbol": remove_currency_symbol,
    "replace_comma_with_dot": replace_comma_with_dot,
    "replace_dot_with_comma": replace_dot_with_comma,
    
    # Boolean transformers
    "boolean_to_yes_no": boolean_to_yes_no,
    "boolean_to_01": boolean_to_01,
    "yes_no_to_boolean": yes_no_to_boolean,
    
    # String manipulation
    "pad_left": pad_left,
    "pad_right": pad_right,
    "first_word": first_word,
    "last_word": last_word,
    "prefix": prefix,
    "suffix": suffix,
    "extract_digits": extract_digits,
    "extract_letters": extract_letters,
    
    # Special formats
    "normalize_phone": normalize_phone,
    "format_ean13": format_ean13,
    
    # Default/Empty handling
    "default_if_empty": default_if_empty,
    "null_to_empty": null_to_empty,
    "empty_to_zero": empty_to_zero,
}


def get_transformer(name: str) -> Callable:
    """Récupère une fonction de transformation par son nom.

    Args:
        name (str): Nom du transformateur.

    Returns:
        Callable: Fonction transformateur.

    Raises:
        ValueError: Si le transformateur n'existe pas dans le registre.

    Examples:
        >>> get_transformer("uppercase")("abc")
        'ABC'
    """
    if name not in TRANSFORMER_REGISTRY:
        available = ", ".join(sorted(TRANSFORMER_REGISTRY.keys()))
        raise ValueError(f"Transformer '{name}' not found. Available transformers:\n{available}")
    return TRANSFORMER_REGISTRY[name]


def register_transformer(name: str, func: Callable):
    """Enregistre un transformateur personnalisé dans le registre.

    Args:
        name (str): Nom du transformateur.
        func (Callable): Fonction transformateur (accepte ``str`` et retourne ``str``).

    Raises:
        ValueError: Si ``func`` n'est pas appelable.

    Examples:
        >>> def my_custom_transformer(value: str) -> str:
        ...     return value.replace("old", "new")
        >>> register_transformer("my_custom", my_custom_transformer)
    """
    if not callable(func):
        raise ValueError(f"Transformer must be callable, got {type(func)}")
    TRANSFORMER_REGISTRY[name] = func


def list_transformers() -> list:
    """Liste tous les transformateurs disponibles.

    Returns:
        list: Liste des noms de transformateurs triés.
    """
    return sorted(TRANSFORMER_REGISTRY.keys())


def get_transformer_info(name: str) -> str:
    """Récupère la documentation d'un transformateur.

    Args:
        name (str): Nom du transformateur.

    Returns:
        str: Docstring du transformateur, ou un message si absente.
    """
    transformer = get_transformer(name)
    return transformer.__doc__ or "No documentation available"


# Utility function to apply multiple transformers in sequence
def chain_transformers(*transformer_names: str) -> Callable:
    """Enchaîne plusieurs transformateurs pour application séquentielle.

    Args:
        *transformer_names (str): Noms des transformateurs à enchaîner.

    Returns:
        Callable: Fonction combinée appliquant chaque transformateur dans l'ordre.

    Examples:
        >>> chained = chain_transformers("strip_whitespace", "uppercase", "truncate")
        >>> chained("  hello world  ")
        'HELLO WORL'
    """
    transformers = [get_transformer(name) for name in transformer_names]
    
    def combined_transformer(value: str) -> str:
        for transformer in transformers:
            value = transformer(value)
        return value
    
    return combined_transformer