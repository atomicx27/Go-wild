import pytest
from examples.fib import get_nth_fibonacci

def test_fib_zero():
    assert get_nth_fibonacci(0) == 0

def test_fib_one():
    assert get_nth_fibonacci(1) == 1

def test_fib_positive():
    assert get_nth_fibonacci(5) == 5
    assert get_nth_fibonacci(10) == 55

def test_fib_negative():
    assert get_nth_fibonacci(-5) == -5
