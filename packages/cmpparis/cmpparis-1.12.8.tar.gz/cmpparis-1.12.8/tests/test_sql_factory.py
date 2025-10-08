import pytest
from cmpparis.odbc import Odbc
from cmpparis.mssql import Mssql
from cmpparis.sql_factory import SqlFactory

class TestSqlFactory:
    
    def test_create_sql_connector_odbc(self):
        sql_factory = SqlFactory()

        sql_connector_odbc = sql_factory.create_sql_connector("odbc", "test_server", "test_database", "test_username", "test_password")

        assert isinstance (sql_connector_odbc, Odbc)

    def test_create_sql_connector_mssql(self):
        sql_factory = SqlFactory()

        sql_connector_mssql = sql_factory.create_sql_connector("mssql", "test_server", "test_database", "test_username", "test_password")

        assert isinstance (sql_connector_mssql, Mssql)

    def test_create_sql_connector_error(self):
        sql_factory = SqlFactory()

        with pytest.raises(ValueError, match="Invalid connector type"):
            sql_factory.create_sql_connector("test", "test_server", "test_database", "test_username", "test_password")
