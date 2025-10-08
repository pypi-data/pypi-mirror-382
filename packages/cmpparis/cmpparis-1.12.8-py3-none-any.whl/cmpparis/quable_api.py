import logging
import requests
import sys

from cmpparis.parameters_utils import get_parameter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class QuableAPI:
    """Client simple pour l'API Quable.

    Ce client gère l'authentification Bearer et expose des méthodes ``get`` et
    ``post`` minimales. Les paramètres peuvent être fournis explicitement ou
    chargés paresseusement via ``get_parameter``.

    Examples:
        Instanciation avec paramètres explicites:

        >>> api = QuableAPI(base_url="https://api.quable.com/v5", api_key="TOKEN")
        >>> isinstance(api.headers["Authorization"].startswith("Bearer "), bool)
        True
    """

    BASE_URL = None  # ← Ne plus appeler get_parameter ici
    API_KEY = None   # ← Ne plus appeler get_parameter ici

    def __init__(self, base_url=None, api_key=None):
        """Initialise le client API Quable.

        Args:
            base_url (str | None): URL de base de l'API Quable.
            api_key (str | None): Jeton d'API (Bearer token).

        Notes:
            Si les paramètres ne sont pas fournis, ils sont récupérés via
            :func:`cmpparis.parameters_utils.get_parameter`.
        """
        # Lazy loading : seulement si on instancie sans paramètres
        if base_url is None:
            from cmpparis.parameters_utils import get_parameter
            base_url = get_parameter("mit", "quabled_api_v5_base_url")
        
        if api_key is None:
            from cmpparis.parameters_utils import get_parameter
            api_key = get_parameter("mit", "quable_token")
        
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def get(self, endpoint, params=None):
        """Effectue une requête GET vers l'API Quable.

        Args:
            endpoint (str): Chemin relatif de l'endpoint (sans slash initial ou final).
            params (dict | None): Paramètres de requête (query string) optionnels.

        Returns:
            dict | list | None: Corps JSON de la réponse si succès, ``None`` en cas d'erreur.

        Raises:
            requests.exceptions.HTTPError: Ré-émise après journalisation si ``raise_for_status`` échoue.
        """
        url = f'{self.base_url}/{endpoint}'

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logger.info(f"Error while making GET request to Quable API : {err}")
        except requests.exceptions.RequestException as err:
            logger.info(f"Error while making GET request to Quable API : {err}")
        except Exception as err:
            logger.info(f"Error while making GET request to Quable API : {err}")

    def post(self, endpoint, data):
        """Effectue une requête POST vers l'API Quable.

        Args:
            endpoint (str): Chemin relatif de l'endpoint.
            data (dict): Corps de la requête à envoyer en JSON.

        Returns:
            dict | list | None: Corps JSON de la réponse si succès, ``None`` en cas d'erreur.

        Raises:
            requests.exceptions.HTTPError: Ré-émise après journalisation si ``raise_for_status`` échoue.
        """
        url = f'{self.base_url}/{endpoint}'

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logger.info(f"Error while making POST request to Quable API : {err}")
        except requests.exceptions.RequestException as err:
            logger.info(f"Error while making POST request to Quable API : {err}")
        except Exception as err:
            logger.info(f"Error while making POST request to Quable API : {err}")