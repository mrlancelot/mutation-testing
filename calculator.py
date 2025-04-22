def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Calculate a raised to the power of b"""
    return a ** b

def square_root(a):
    """Calculate the square root of a"""
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return a ** 0.5

def absolute(a):
    """Return the absolute value of a"""
    return abs(a)

def modulo(a, b):
    """Return a modulo b"""
    if b == 0:
        raise ValueError("Cannot compute modulo with divisor 0")
    return a % b

def factorial(n):
    """Calculate the factorial of n"""
    if not isinstance(n, int):
        raise TypeError("Factorial only defined for integers")
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def gcd(a, b):
    """Calculate the greatest common divisor of a and b"""
    if not (isinstance(a, int) and isinstance(b, int)):
        raise TypeError("GCD only defined for integers")
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a 