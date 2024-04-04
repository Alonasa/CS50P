import pytest
from main import check_deadline


def test_get_deadline():
    with pytest.raises(ValueError):
        check_deadline("dsougwego")
    with pytest.raises(ValueError):
        check_deadline("04-32-32")
    assert check_deadline("2024-03-02") == "2024-03-02"
    assert check_deadline("2024-03-02") == "2024-03-02"

