import pytest
from unittest.mock import patch, MagicMock
from cmpparis.odbc import Odbc

class TestOdbc:

    @pytest.fixture
    def odbc_instance(self):
        return Odbc(
            server="test_server",
            database="test_db",
            username="test_user",
            password="test_pass"
        )

    def test_init(self, odbc_instance):
        assert odbc_instance.server == "test_server"
        assert odbc_instance.database == "test_db"
        assert odbc_instance.username == "test_user"
        assert odbc_instance.password == "test_pass"
        assert not hasattr(odbc_instance, 'port')

    def test_init_with_port(self):
        odbc = Odbc(
            server="test_server",
            database="test_db",
            username="test_user",
            password="test_pass",
            port=1433
        )
        assert odbc.port == 1433

    @patch('pyodbc.connect')
    def test_connect_success(self, mock_connect, odbc_instance):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        result = odbc_instance.connect("SQL Server")

        expected_connection_string = (
            "DRIVER={SQL Server};"
            "SERVER=test_server;"
            "DATABASE=test_db;"
            "UID=test_user;"
            "PWD=test_pass;"
        )
        mock_connect.assert_called_once_with(expected_connection_string)
        assert result == mock_connection

    @patch('pyodbc.connect')
    def test_connect_failure(self, mock_connect, odbc_instance, capsys):
        mock_connect.side_effect = Exception("Connection failed")

        result = odbc_instance.connect("SQL Server")

        assert result is None
        captured = capsys.readouterr()
        assert "Error connecting to SQL Server: Connection failed" in captured.out

if __name__ == "__main__":
    pytest.main()