import csv
import openpyxl
import pytest

from unittest.mock import patch, MagicMock
from cmpparis.file import File

@pytest.fixture
def file():
    return File('test.txt')

# Assert that the correct file name is returned
def test_file_name(file):
    assert file.name == 'test.txt'

# Assert that the correct extension is returned
def test_get_file_extension(file):
    assert file.get_extension() == 'txt'

# Test that an exception is raised when the file does not exist
def test_read_file_to_dataframe_file_not_found():
    file = File('nonexistent.csv')

    with pytest.raises(Exception, match=r"The CSV file was not found : .*"):
        file.read_file_to_dataframe()

# Test that an exception is raised when the file has an unsupported extension
def test_read_file_to_dataframe_invalid_extension(file):
    with pytest.raises(Exception, match="Unsupported file extension"):
        file.read_file_to_dataframe()

# Test than an exception is raised when the csv file does not contain any column
def test_read_file_to_dataframe_csv_no_columns(tmp_path):
    with open(tmp_path / "data.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        csv_writer.writerow([])

    file_path = tmp_path / "data.csv"
    file = File(str(file_path))

    with pytest.raises(Exception, match=r".* No columns to parse from file"):
        file.read_file_to_dataframe()

# Test that an exception is raised when the dataframe is empty
def test_read_file_to_dataframe_csv_empty_dataframe(tmp_path):
    with open(tmp_path / "data.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        csv_writer.writerow(['col1', 'col2'])

    file_path = tmp_path / "data.csv"

    file_obj = File(str(file_path))

    with pytest.raises(Exception, match="The dataframe is empty"):
        file_obj.read_file_to_dataframe()

def test_read_file_to_dataframe_csv(tmp_path):
    with open(tmp_path / "data.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        csv_writer.writerow(['col1', 'col2'])
        csv_writer.writerow(['val1', 'val2'])

    file_path = tmp_path / "data.csv"

    file_obj = File(str(file_path))

    df = file_obj.read_file_to_dataframe()

    assert df.shape == (1, 2)
    assert list(df.columns) == ['col1', 'col2']
    assert list(df['col1'])[0] == 'val1'
    assert list(df['col2'])[0] == 'val2'
    assert list(df.index) == [0]

# Test that an exception is raised when the dataframe is empty
def test_read_file_to_dataframe_excel_empty(tmp_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    data = []
    sheet.append(data)

    workbook.save(tmp_path / "data.xlsx")

    file_path = tmp_path / "data.xlsx"

    file_obj = File(str(file_path))

    with pytest.raises(Exception, match=r"The dataframe is empty"):
        file_obj.read_file_to_dataframe()

def test_read_file_to_dataframe_excel(tmp_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    data = [
        ['col1', 'col2'],
        ['val1', 'val2']
    ]

    for row in data:
        sheet.append(row)

    workbook.save(tmp_path / "data.xlsx")

    file_path = tmp_path / "data.xlsx"

    file_obj = File(str(file_path))

    df = file_obj.read_file_to_dataframe()

    assert df.shape == (1, 2)
    assert list(df.columns) == ['col1', 'col2']
    assert list(df['col1'])[0] == 'val1'
    assert list(df['col2'])[0] == 'val2'
    assert list(df.index) == [0]

