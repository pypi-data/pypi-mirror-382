import paramiko
import sys

from cmpparis.ses_utils import *

class FTP:
    """Client SFTP minimal basé sur ``paramiko``.

    Fournit des opérations simples: connexion, changement de dossier,
    listage, upload, download et fermeture.
    """

    def __init__(self, host, port=22):
        """Initialise la connexion SFTP (sans authentification).

        Args:
            host (str): Nom d'hôte ou IP du serveur SFTP.
            port (int): Port SFTP (par défaut: 22).
        """
        self.host = host
        self.port = port
        self.transport = paramiko.Transport((self.host, self.port))
        self.sftp = None

    def set_working_directory(self, directory):
        """Change le répertoire de travail sur le serveur SFTP.

        Args:
            directory (str): Chemin distant.
        """
        try:
            self.sftp.chdir(directory)
        except Exception as e:
            subject = "FTP - working directory setting error"
            error_message = f"Error while setting working directory on SFTP server: {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    def login(self, username, passwd):
        """S'authentifie et ouvre une session SFTP.

        Args:
            username (str): Nom d'utilisateur.
            passwd (str): Mot de passe.
        """
        try:
            self.transport.connect(username=username, password=passwd)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except Exception as e:
            subject = "FTP - login error"
            error_message = f"Error while connecting to SFTP server: {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    def list_files(self):
        """Liste les fichiers dans le répertoire courant du serveur.

        Returns:
            list[str]: Noms de fichiers.
        """
        try:
            return self.sftp.listdir()
        except Exception as e:
            subject = "FTP - listing files error"
            error_message = f"Error while listing files on SFTP server: {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    def upload_file(self, localfile, remotefile):
        """Transfère un fichier local vers le serveur SFTP.

        Args:
            localfile (str): Chemin du fichier local.
            remotefile (str): Chemin distant de destination.
        """
        try:
            self.sftp.put(localfile, remotefile)
        except Exception as e:
            subject = "FTP - file upload error"
            error_message = f"Error while uploading file to SFTP server: {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    def download_file(self, remotefile, localfile):
        """Télécharge un fichier depuis le serveur SFTP.

        Args:
            remotefile (str): Chemin distant du fichier.
            localfile (str): Chemin local de destination.
        """
        try:
            self.sftp.get(remotefile, localfile)
        except Exception as e:
            subject = "FTP - file download error"
            error_message = f"Error while downloading file from SFTP server: {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    def close(self):
        """Ferme la session SFTP et la connexion sous-jacente."""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
