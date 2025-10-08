from .sql_interface import SqlInterface

import pyodbc


class Odbc(SqlInterface):
    """Client générique SQL via ODBC (``pyodbc``)."""

    def __init__(self, server, database, username, password, port = None):
        """Initialise les paramètres de connexion ODBC.

        Args:
            server (str): Hôte/instance.
            database (str): Nom de la base de données.
            username (str): Nom d'utilisateur.
            password (str): Mot de passe.
            port (int | None): Port optionnel.
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        if port is not None:
            self.port = port

    def connect(self, driver):
        """Ouvre une connexion via une chaîne ODBC construite.

        Args:
            driver (str): Nom du driver ODBC installé (ex: ``ODBC Driver 18 for SQL Server``).

        Returns:
            pyodbc.Connection | None: Connexion ouverte ou ``None`` en cas d'erreur.
        """
        try:
            connection_string = "DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};".format(
                driver=driver,
                server=self.server,
                database=self.database,
                username=self.username,
                password=self.password
            )

            return pyodbc.connect(connection_string)
        except Exception as e:
            print(f"Error connecting to SQL Server: {e}")

    def disconnect(self, connection):
        """Ferme la connexion ODBC fournie.

        Args:
            connection (pyodbc.Connection): Connexion à fermer.
        """
        try:
            connection.close()
        except Exception as e:
            print(f"Error disconnecting from SQL Server: {e}")