from main import validate_email


def test_validate_email():
    assert validate_email("hello@mail") == False
    assert validate_email("hello@mail.com") == True
    assert validate_email("HELLO@mail.com") == True
    assert validate_email("hello.mail.com") == False
