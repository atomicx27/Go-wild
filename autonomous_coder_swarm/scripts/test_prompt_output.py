def print_fibonacci_numbers():
    """Prints the first 10 Fibonacci numbers."""
    a, b = 0, 1
    for _ in range(10):
        print(a)
        a, b = b, a + b

# Call the function to print the first 10 Fibonacci numbers
print_fibonacci_numbers()