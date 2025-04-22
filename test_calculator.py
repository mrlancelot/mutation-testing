import pytest
from calculator import add, subtract, multiply, divide, power, square_root, absolute, modulo, factorial, gcd

# Basic functionality tests
def test_add_basic():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(-5, -7) == -12

def test_subtract_basic():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(0, 0) == 0
    assert subtract(-5, -3) == -2
    assert subtract(-5, 3) == -8

def test_multiply_basic():
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6
    assert multiply(-2, -3) == 6
    assert multiply(0, 5) == 0
    assert multiply(5, 0) == 0

def test_divide_basic():
    assert divide(6, 3) == 2
    assert divide(7, 2) == 3.5
    assert divide(-6, 3) == -2
    assert divide(-6, -3) == 2
    assert divide(0, 5) == 0

# Edge case tests
def test_large_numbers():
    assert add(10**6, 10**6) == 2 * 10**6
    assert subtract(10**6, 10**6) == 0
    assert multiply(10**6, 2) == 2 * 10**6
    assert divide(10**6, 10**3) == 10**3

def test_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(5, 0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(-5, 0)

# Mutation testing focused tests
def test_add_mutations():
    """Specific tests to catch potential mutations in add function"""
    # Catches mutation of + to -
    assert add(5, 3) == 8
    assert add(5, 3) != 2
    
    # Catches mutation of order of operands
    x, y = 5, 7
    assert add(x, y) == x + y

def test_subtract_mutations():
    """Specific tests to catch potential mutations in subtract function"""
    # Catches mutation of - to +
    assert subtract(5, 3) == 2
    assert subtract(5, 3) != 8
    
    # Catches mutation of order of operands
    x, y = 5, 3
    assert subtract(x, y) == x - y
    assert subtract(x, y) != y - x

def test_multiply_mutations():
    """Specific tests to catch potential mutations in multiply function"""
    # Catches mutation of * to /
    assert multiply(10, 2) == 20
    assert multiply(10, 2) != 5
    
    # Catches mutation of * to +
    assert multiply(5, 3) == 15
    assert multiply(5, 3) != 8
    
    # Catches mutation to 0 or 1
    assert multiply(7, 3) != 0
    assert multiply(7, 3) != 1

def test_divide_mutations():
    """Specific tests to catch potential mutations in divide function"""
    # Catches mutation of / to *
    assert divide(10, 2) == 5
    assert divide(10, 2) != 20
    
    # Catches mutation of / to -
    assert divide(10, 2) != 8
    
    # Catches mutation of condition check
    with pytest.raises(ValueError):
        divide(10, 0)
        
    # Catches precision issues
    assert divide(1, 3) == pytest.approx(0.333333, 0.0001)

def test_add_edge_cases():
    """Edge cases for the add function."""
    assert add(0, 0) == 0
    assert add(100, -100) == 0
    assert add(-1, -1) == -2
    assert add(10**6, 10**6) == 2 * 10**6

def test_subtract_edge_cases():
    """Edge cases for the subtract function."""
    assert subtract(0, 0) == 0
    assert subtract(100, 100) == 0
    assert subtract(-1, -1) == 0
    assert subtract(-1, 1) == -2
    assert subtract(10**6, 10**6) == 0

def test_multiply_edge_cases():
    """Edge cases for the multiply function."""
    assert multiply(0, 5) == 0
    assert multiply(5, 0) == 0
    assert multiply(1, 100) == 100
    assert multiply(-1, 10) == -10
    assert multiply(-2, -3) == 6

def test_divide_edge_cases():
    """Edge cases for the divide function."""
    assert divide(10, 2) == 5
    assert divide(10, 3) == pytest.approx(3.333333, 0.01)
    assert divide(-10, 2) == -5
    assert divide(-10, -2) == 5
    assert divide(0, 5) == 0
    
    with pytest.raises(ValueError):
        divide(10, 0)

# Tests for power function
def test_power_basic():
    """Basic tests for the power function"""
    assert power(2, 3) == 8
    assert power(5, 2) == 25
    assert power(10, 0) == 1
    assert power(1, 10) == 1
    assert power(0, 5) == 0

def test_power_edge_cases():
    """Edge cases for the power function"""
    assert power(2, -1) == 0.5
    assert power(-2, 2) == 4
    assert power(-2, 3) == -8
    assert power(4, 0.5) == 2

def test_power_mutations():
    """Tests to catch potential mutations in power function"""
    assert power(2, 3) != 5  # Catches ** changed to +
    assert power(3, 2) != 6  # Catches ** changed to *
    assert power(3, 2) == 9

# Tests for square_root function
def test_square_root_basic():
    """Basic tests for the square_root function"""
    assert square_root(4) == 2
    assert square_root(9) == 3
    assert square_root(0) == 0
    assert square_root(1) == 1
    assert square_root(2) == pytest.approx(1.414, 0.001)

def test_square_root_edge_cases():
    """Edge cases for the square_root function"""
    with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
        square_root(-1)
    assert square_root(10**10) == 10**5

def test_square_root_mutations():
    """Tests to catch potential mutations in square_root function"""
    assert square_root(4) != 4  # Catches ** 0.5 changed to ** 1
    assert square_root(9) != 3.5  # Catches precision issues
    assert square_root(16) == 4

# Tests for absolute function
def test_absolute_basic():
    """Basic tests for the absolute function"""
    assert absolute(5) == 5
    assert absolute(-5) == 5
    assert absolute(0) == 0

def test_absolute_edge_cases():
    """Edge cases for the absolute function"""
    assert absolute(-9999) == 9999
    assert absolute(9999) == 9999
    assert absolute(-0) == 0

def test_absolute_mutations():
    """Tests to catch potential mutations in absolute function"""
    # Test that the sign is actually changing
    assert absolute(-5) != -5
    
    # Test that it's not just returning the operand
    assert absolute(-10) != -10
    assert absolute(-10) == 10

# Tests for modulo function
def test_modulo_basic():
    """Basic tests for the modulo function"""
    assert modulo(10, 3) == 1
    assert modulo(10, 2) == 0
    assert modulo(5, 7) == 5
    assert modulo(0, 5) == 0

def test_modulo_edge_cases():
    """Edge cases for the modulo function"""
    assert modulo(-10, 3) == 2  # Python's modulo behavior with negative numbers
    assert modulo(10, -3) == -2
    
    with pytest.raises(ValueError, match="Cannot compute modulo with divisor 0"):
        modulo(10, 0)

def test_modulo_mutations():
    """Tests to catch potential mutations in modulo function"""
    assert modulo(10, 3) != 3.33  # Catches % changed to /
    assert modulo(10, 3) == 1
    assert modulo(5, 2) != 10  # Catches % changed to *

# Tests for factorial function
def test_factorial_basic():
    """Basic tests for the factorial function"""
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(2) == 2
    assert factorial(3) == 6
    assert factorial(4) == 24
    assert factorial(5) == 120

def test_factorial_edge_cases():
    """Edge cases for the factorial function"""
    with pytest.raises(ValueError, match="Factorial not defined for negative numbers"):
        factorial(-1)
    
    with pytest.raises(TypeError, match="Factorial only defined for integers"):
        factorial(3.5)
    
    # Test a larger factorial
    assert factorial(10) == 3628800

def test_factorial_mutations():
    """Tests to catch potential mutations in factorial function"""
    assert factorial(4) != 4  # Catches return n
    assert factorial(0) == 1  # Special case handling
    assert factorial(5) == 120

# Tests for gcd function
def test_gcd_basic():
    """Basic tests for the gcd function"""
    assert gcd(8, 12) == 4
    assert gcd(15, 25) == 5
    assert gcd(7, 11) == 1  # Coprime numbers
    assert gcd(0, 5) == 5
    assert gcd(5, 0) == 5

def test_gcd_edge_cases():
    """Edge cases for the gcd function"""
    assert gcd(-8, 12) == 4  # Should handle negative numbers
    assert gcd(8, -12) == 4
    assert gcd(-8, -12) == 4
    
    with pytest.raises(TypeError, match="GCD only defined for integers"):
        gcd(3.5, 7)
    
    with pytest.raises(TypeError, match="GCD only defined for integers"):
        gcd(3, 7.5)

def test_gcd_mutations():
    """Tests to catch potential mutations in gcd function"""
    assert gcd(8, 12) != 8  # Catches return a
    assert gcd(8, 12) != 12  # Catches return b
    assert gcd(8, 12) == 4

# Additional tests to catch surviving mutations

def test_square_root_error_message():
    """Tests that the proper error message is raised for negative inputs to square_root"""
    try:
        square_root(-1)
        assert False, "Expected ValueError to be raised"
    except ValueError as e:
        # Check exact error message text to catch message mutations
        assert str(e) == "Cannot calculate square root of negative number"

def test_modulo_error_message():
    """Tests that the proper error message is raised for zero divisor in modulo"""
    try:
        modulo(10, 0)
        assert False, "Expected ValueError to be raised"
    except ValueError as e:
        # Check exact error message text to catch message mutations
        assert str(e) == "Cannot compute modulo with divisor 0"

def test_modulo_vs_division():
    """Tests that modulo is different from division"""
    for a, b in [(10, 3), (7, 2), (20, 6)]:
        # For these pairs, modulo and division give different results
        assert modulo(a, b) != a / b
        # Specific check to ensure modulo is working correctly
        assert modulo(a, b) == a % b

def test_factorial_type_error_message():
    """Tests that the proper error message is raised for non-integer inputs to factorial"""
    try:
        factorial(3.5)
        assert False, "Expected TypeError to be raised"
    except TypeError as e:
        # Check exact error message text to catch message mutations
        assert str(e) == "Factorial only defined for integers"

def test_factorial_value_error_message():
    """Tests that the proper error message is raised for negative inputs to factorial"""
    try:
        factorial(-1)
        assert False, "Expected ValueError to be raised"
    except ValueError as e:
        # Check exact error message text to catch message mutations
        assert str(e) == "Factorial not defined for negative numbers"

def test_factorial_special_cases():
    """Tests factorial's handling of special cases (0 and 1)"""
    # These should both return 1, testing the or condition with both inputs
    assert factorial(0) == 1
    assert factorial(1) == 1
    
    # Test that the behavior is correct regardless of how the condition is formed
    # (catches if n == 0 or n == 1 -> if n == 0 and n == 1, etc.)
    assert isinstance(factorial(0), int) and factorial(0) == 1
    assert isinstance(factorial(1), int) and factorial(1) == 1
    
    # Test that return value is exactly 1, not True (which would be == 1)
    assert factorial(0) is not True
    assert type(factorial(0)) is int

def test_special_return_values():
    """Tests that functions return the exact expected values, not just equivalent values like True"""
    # Test that return values are exact, not just equivalent (like 1 == True)
    assert type(factorial(0)) is int
    assert factorial(0) is not True
    
    assert type(factorial(1)) is int
    assert factorial(1) is not True
    
    assert type(gcd(0, 0)) is int
    assert gcd(0, 0) is not True
    
    assert type(modulo(10, 5)) is int
    assert modulo(10, 5) is not True

