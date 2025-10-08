import boto3
import os
import sys

from botocore.exceptions import ClientError

from cmpparis.parameters_utils import *
from cmpparis.ses_utils import *
from datetime import datetime

class S3:
    """Client utilitaire pour interagir avec un bucket S3."""

    def __init__(self, aws_region_name, aws_bucket_name):
        """Initialise le client S3.

        Args:
            aws_region_name (str): Région AWS.
            aws_bucket_name (str): Nom du bucket.
        """
        self.aws_region_name = aws_region_name
        self.aws_bucket_name = aws_bucket_name
        self.s3 = boto3.client('s3', region_name=aws_region_name)

    # Function to download file from S3 bucket
    def download_file_from_s3(self, s3_key, local_filename):
        """Télécharge un fichier depuis S3 vers un fichier local.

        Args:
            s3_key (str): Clé de l'objet dans le bucket.
            local_filename (str): Chemin de sortie local.

        Returns:
            bool: ``True`` si succès.
        """
        try:
            self.s3.download_file(self.aws_bucket_name, s3_key, local_filename)
            print("The file has been successfully downloaded from the S3 bucket")
            return True
        except ClientError as e:
            subject = "S3 - File download error"
            error_message = f"Error while downloading the CSV file from the S3 bucket : {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    # Function to get file from S3 bucket
    def get_file_from_s3(self, s3_key):
        """Récupère un fichier S3 et renvoie son contenu en texte (UTF-8).

        Args:
            s3_key (str): Clé de l'objet.

        Returns:
            str: Contenu du fichier en UTF-8.
        """
        try:
            response = self.s3.get_object(Bucket=self.aws_bucket_name, Key=s3_key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            subject = "S3 - Getting file error"
            error_message = f"Error while getting the file from S3 : {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    # Function to get all files from S3 bucket location
    def get_files_from_s3(self, s3_key):
        """Liste les clés d'objets sous un préfixe donné.

        Args:
            s3_key (str): Préfixe ("dossier") S3.

        Returns:
            list[str]: Liste des clés.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=self.aws_bucket_name, Prefix=s3_key)
            files = []
            for obj in response.get('Contents', []):
                files.append(obj['Key'])
            return files
        except ClientError as e:
            subject = "S3 - Getting files error"
            error_message = f"Error while getting the files from S3 : {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    # Function to upload a file to S3
    def upload_file_to_s3(self, local_filename, s3_key = None):
        """Charge un fichier local vers S3.

        Args:
            local_filename (str): Chemin du fichier local.
            s3_key (str | None): Clé de destination. Par défaut, le nom du fichier local.

        Returns:
            bool: ``True`` si succès.
        """
        try:
            if (s3_key is None):
                s3_key = os.path.basename(local_filename)

            self.s3.upload_file(local_filename, self.aws_bucket_name, s3_key)
            print("File uploaded and archived to S3")
            return True
        except ClientError as e:
            subject = "S3 - File upload error"
            error_message = f"Error while uploading file to S3 : {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    # Function to delete file from S3 bucket
    def delete_file_from_s3(self, s3_key):
        """Supprime un objet dans S3.

        Args:
            s3_key (str): Clé de l'objet.

        Returns:
            bool: ``True`` si succès.
        """
        try:
            self.s3.delete_object(Bucket=self.aws_bucket_name, Key=s3_key)
            print("File deleted from S3")
            return True
        except ClientError as e:
            subject = "S3 - File deletion error"
            error_message = f"Error while deleting file from S3 : {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)

    def archive_file_in_s3(self, prefix, s3_key):
        """Archive un objet à un chemin horodaté dans S3.

        L'objet est copié sous ``archive/{prefix}/YYYY/MM/DD/<name>_<timestamp>.ext``.

        Args:
            prefix (str): Préfixe logique (projet/process).
            s3_key (str): Clé de l'objet source.

        Returns:
            bool: ``True`` si succès.
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        filename = os.path.basename(s3_key)
        name, extension = os.path.splitext(filename)
        archived_filename = f"{name}_{timestamp}{extension}"

        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

        archive_prefix = f"archive/{prefix.rstrip('/')}/{year}/{month}/{day}/"
        archive_key = f"{archive_prefix}{archived_filename}"

        try:
            self.s3.copy_object(
                Bucket=self.aws_bucket_name,
                CopySource={'Bucket': self.aws_bucket_name, 'Key': s3_key},
                Key=archive_key
            )
            print(f"Archived file %s to %s", s3_key, archive_key)
            return True
        except ClientError as e:
            subject = "S3 - File archiving error"
            error_message = f"Error while archiving file in S3 : {e}"
            print(error_message)
            send_email_to_support(subject, error_message)

            sys.exit(1)