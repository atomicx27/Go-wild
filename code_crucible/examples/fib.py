def get_nth_fibonacci(n):
    if n <= 1:
        return n
    else:
        return get_nth_fibonacci(n - 1) + get_nth_fibonacci(n - 2)
