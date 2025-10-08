import pandas as pd

from cmpparis.ses_utils import *

supported_extensions = ['csv', 'xlsx']

class File:
    """Abstraction simple d'un fichier tabulaire (CSV/XLSX).

    Cette classe offre des méthodes pour charger un fichier CSV ou Excel dans un
    ``pandas.DataFrame``, extraire des messages depuis une feuille dédiée et
    récupérer des méta-informations de base.
    """

    def __init__(self, name):
        """Initialise l'objet fichier.

        Args:
            name (str): Chemin/nom du fichier.
        """
        self.name = name

    def __str__(self):
        """Retourne une représentation textuelle du fichier."""
        return f"{self.name}"

    def __repr__(self):
        """Retourne une représentation développeur du fichier."""
        return f"File({self.name})"

    def get_extension(self):
        """Renvoie l'extension du fichier.

        Returns:
            str: Extension du fichier (ex: ``csv``, ``xlsx``).
        """
        return self.name.split(".")[-1]

    def get_name(self):
        """Renvoie le nom/chemin du fichier.

        Returns:
            str: Nom du fichier.
        """
        return self.name

    def csv_to_dataframe(self):
        """Charge un fichier CSV dans un ``pandas.DataFrame``.

        Returns:
            pandas.DataFrame: Données lues.

        Raises:
            Exception: Si le fichier est introuvable ou en cas d'erreur de lecture.
        """
        try:
            #read the file and convert it to a DataFrame
            with open(self.name, 'r', errors="ignore") as csv_file:
                csv_reader = pd.read_csv(filepath_or_buffer=csv_file, delimiter=';', dtype=object)

            return csv_reader
        except FileNotFoundError as e:
            raise Exception(f"The CSV file was not found : {e}")
        except Exception as e:
            raise Exception(f"Error while reading the CSV file : {e}")

    def excel_to_dataframe(self, sheet_name=None):
        """Charge un fichier Excel dans un ``pandas.DataFrame``.

        Args:
            sheet_name (str | None): Nom de la feuille à lire. Si ``None``, la première feuille sera lue.

        Returns:
            pandas.DataFrame: Données lues.

        Raises:
            Exception: Si le fichier est introuvable ou en cas d'erreur de lecture.
        """
        try:
            if (sheet_name != None):
                excel_reader = pd.read_excel(io=self.name, sheet_name=sheet_name)
            else:
                excel_reader = pd.read_excel(io=self.name)

            return excel_reader
        except FileNotFoundError as e:
            raise Exception(f"The Excel file was not found : {e}")
        except Exception as e:
            raise Exception(f"Error while reading the Excel file : {e}")

    def extract_message_from_code(self, code):
        """Extrait un message depuis l'onglet ``MESSAGES`` d'un fichier Excel.

        Args:
            code (str | int): Code du message à rechercher.

        Returns:
            Any: Valeur du message correspondant au code.
        """
        msg_list = self.excel_to_dataframe('MESSAGES')

        message = msg_list.loc[msg_list['code'] == code]

        return message['message'].values[0]

    #function that reads the file and sets the content inside a DataFrame according to its extension
    #supported extensions are : csv, xlsx
    #handle exceptions
    def read_file_to_dataframe(self, sheet=None):
        """Lit le fichier et renvoie un ``pandas.DataFrame`` selon l'extension.

        Extensions supportées: ``csv``, ``xlsx``.

        Args:
            sheet (str | None): Nom de la feuille Excel à lire, si applicable.

        Returns:
            pandas.DataFrame: Données lues.

        Raises:
            Exception: Si l'extension n'est pas supportée ou si le DataFrame est vide.
        """
        if (self.get_extension() not in supported_extensions):
            raise Exception("Unsupported file extension")

        file_extension = self.get_extension()

        match file_extension:
            case "csv":
                df = self.csv_to_dataframe()

                if (df.size == 0):
                    raise Exception("The dataframe is empty")

                return df
            case _:
                df = self.excel_to_dataframe(sheet)

                if (df.size == 0):
                    raise Exception("The dataframe is empty")

                return df