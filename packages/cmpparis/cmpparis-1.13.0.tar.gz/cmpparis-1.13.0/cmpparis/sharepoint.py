import io
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File as SharePointFile

class Sharepoint:
    """Client minimal pour interagir avec SharePoint (Office 365)."""

    def __init__(self, site_url, site_path, client_id, client_secret):
        """Initialise le contexte SharePoint avec authentification applicative.

        Args:
            site_url (str): URL du site SharePoint (racine).
            site_path (str): Chemin du sous-site/collection.
            client_id (str): Application (client) ID.
            client_secret (str): Secret d'application.
        """
        self.site_url = site_url
        self.site_path = site_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.ctx = ClientContext(f"{self.site_url}/{self.site_path}").with_credentials(ClientCredential(self.client_id, self.client_secret))

    def get_context(self):
        """Renvoie le contexte SharePoint initialisé."""
        return self.ctx

    def download_file(self, file_location, local_file_path):
        """Télécharge un fichier SharePoint vers un fichier local.

        Args:
            file_location (str): URL serveur relative du fichier.
            local_file_path (str): Chemin local de destination.
        """
        with open(local_file_path, 'wb') as local_file:
            self.ctx.web.get_file_by_server_relative_url(file_location).download(local_file).execute_query()

    def get_files(self, folder_path):
        """Liste les fichiers d'un dossier SharePoint.

        Args:
            folder_path (str): URL serveur relative du dossier.

        Returns:
            list: Liste des objets fichiers.
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
        files = folder.files
        self.ctx.load(files)
        self.ctx.execute_query()
        return files
    
    def read_file(self, file_location):
        """Lit un fichier SharePoint et retourne un flux binaire en mémoire.

        Args:
            file_location (str): URL serveur relative du fichier.

        Returns:
            io.BytesIO: Flux binaire positionné au début.
        """
        response = SharePointFile.open_binary(self.ctx, file_location)

        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)

        return bytes_file_obj
    
    def upload_file(self, folder_path, filename):
        """Charge un fichier local vers un dossier SharePoint.

        Args:
            folder_path (str): URL serveur relative du dossier.
            filename (str): Chemin du fichier local à charger.
        """
        target_folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)

        with open(filename, 'rb') as file_content:
            content = file_content.read()
            target_folder.upload_file(filename, content).execute_query()