####################################################
# test_utils.py for the 'cmpparis' library
# Created by: Sofiane Charrad
####################################################

from cmpparis.utils import *

def test_format_date():
    assert format_date("2023-05-15 12:05:38", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y") == "15/05/2023"

def test_current_datetime_formatted():
    assert get_current_datetime_formatted("%Y-%m-%d %H:%M:%S") == datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def test_remove_diacritics():
    assert remove_diacritics("àéîôû") == "aeiou"

def test_replace():
    assert replace("a replace test; test a replace", "[;&~|`\\^¨?]", "") == "a replace test test a replace"

def test_check_email():
    assert check_email("test@test.com") == True
    assert check_email("test@test") == False
    assert check_email("test@") == False
    assert check_email("test@test.com.fr") == True
    assert check_email("test@test.com.fr.fr") == True

def test_check_encoding():
    assert check_encoding("test") == True
    assert check_encoding("testŸÌ╝+Üþ") == False