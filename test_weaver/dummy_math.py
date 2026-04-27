def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def complex_operation(x):
    # Some complex math logic
    if x < 0:
        return 0
    return (x * 2) + 5
