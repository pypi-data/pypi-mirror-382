import pytest
from unittest.mock import patch, MagicMock
from cmpparis.mssql import Mssql

class TestMssql:

    @pytest.fixture
    def mssql_instance(self):
        return Mssql(
            server="test_server",
            database="test_db",
            username="test_user",
            password="test_pass"
        )

    def test_init(self, mssql_instance):
        assert mssql_instance.server == "test_server"
        assert mssql_instance.database == "test_db"
        assert mssql_instance.username == "test_user"
        assert mssql_instance.password == "test_pass"
        assert not hasattr(mssql_instance, 'port')

    def test_init_with_port(self):
        odbc = Mssql(
            server="test_server",
            database="test_db",
            username="test_user",
            password="test_pass",
            port=1433
        )
        assert odbc.port == 1433

    @patch('pymssql.connect')
    def test_connect(self, mock_connect, mssql_instance):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        result = mssql_instance.connect()

        mock_connect.assert_called_once_with(server="test_server", database="test_db", user="test_user", password="test_pass")
        assert result == mock_connection

    @patch('cmpparis.mssql.pymssql.connect', side_effect=Exception('Test exception'))
    def test_connect_exception(self, mock_connect, mssql_instance, capsys):
        result = mssql_instance.connect()
        
        assert result is None
        captured = capsys.readouterr()
        assert "Error connecting to MSSQL server: Test exception" in captured.out

    @patch('cmpparis.mssql.pymssql.connect')
    def test_disconnect(self, mock_connect, mssql_instance):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connection = mssql_instance.connect()
        mssql_instance.disconnect(connection)

        mock_connection.close.assert_called_once()

    @patch('cmpparis.mssql.pymssql.connect')
    def test_disconnect_exception(self, mock_connect, mssql_instance, capsys):
        mock_connection = MagicMock()
        mock_connection.close.side_effect = Exception('Test exception')
        mock_connect.return_value = mock_connection

        result = mssql_instance.disconnect(mock_connection)

        assert result is None
        captured = capsys.readouterr()
        assert "Error disconnecting from MSSQL server: Test exception" in captured.out