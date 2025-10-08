from .sql_interface import SqlInterface

import pymssql


class Mssql(SqlInterface):
    """Client simplifié pour SQL Server via ``pymssql``.

    Examples:
        >>> conn = Mssql('localhost', 'db', 'user', 'pwd').connect()
        >>> conn is None or hasattr(conn, 'cursor')
        True
    """

    def __init__(self, server, database, username, password, port = None):
        """Initialise les paramètres de connexion.

        Args:
            server (str): Hôte/instance SQL Server.
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

    def connect(self):
        """Ouvre une connexion ``pymssql``.

        Returns:
            pymssql.Connection | None: Connexion active ou ``None`` en cas d'erreur.
        """
        try:
            return pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
        except Exception as e:
            print(f"Error connecting to MSSQL server: {e}")

    def disconnect(self, connection):
        """Ferme la connexion fournie.

        Args:
            connection (pymssql.Connection): Connexion à fermer.
        """
        try:
            connection.close()
        except Exception as e:
            print(f"Error disconnecting from MSSQL server: {e}")
