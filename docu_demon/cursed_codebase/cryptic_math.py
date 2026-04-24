def f(x, y):
    if y == 0: return 1
    elif y % 2 == 0:
        t = f(x, y//2)
        return t*t
    else:
        return x * f(x, y-1)

def c(n, k):
    if k == 0 or k == n: return 1
    return c(n-1, k-1) + c(n-1, k)
