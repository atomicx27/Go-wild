import pytest
from dummy_math import add, divide, complex_operation

def test_add():
    assert add(2, 3) == 5  # Fixed

def test_divide():
    assert divide(10, 2) == 5

def test_complex():
    assert complex_operation(-1) == 0