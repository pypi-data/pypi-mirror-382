from networking_utils import add_two_number

def test_add_two_number_ints():
    assert add_two_number(2, 3) == 5

def test_add_two_number_floats():
    assert add_two_number(2.5, 0.5) == 3.0
