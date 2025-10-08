class SqlFactory:
    """Fabrique de connecteurs SQL (ODBC, MSSQL)."""

    @staticmethod
    def create_sql_connector(connector_type, server, database, username, password):
        """Crée une instance de connecteur SQL selon le type demandé.

        Args:
            connector_type (str): ``"odbc"`` ou ``"mssql"``.
            server (str): Hôte/instance.
            database (str): Base de données.
            username (str): Utilisateur.
            password (str): Mot de passe.

        Returns:
            Any: Instance de ``Odbc`` ou ``Mssql``.

        Raises:
            ValueError: Si ``connector_type`` est invalide.
        """
        if connector_type == "odbc":
            from .odbc import Odbc

            return Odbc(server, database, username, password)
        elif connector_type == "mssql":
            from .mssql import Mssql

            return Mssql(server, database, username, password)
        else:
            raise ValueError("Invalid connector type")