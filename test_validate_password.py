from main import validate_password


def test_validate_password():
    assert validate_password("1") == False
    assert validate_password("kdskd") == False
    assert validate_password("11111111") == False
    assert validate_password(".1111111") == False
    assert validate_password("dsek3.dskdjs") == True
    assert validate_password("3948A?dksd") == True
    assert validate_password("dsk.ds_32/dsdkwe") == True
    assert validate_password("<ds>k.ds_32/ds") == True
