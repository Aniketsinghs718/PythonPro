def factorial(n):
    try:
        # Check if n is an integer
        if not isinstance(n, int):
            raise ValueError("Input must be an integer.")
        
        # Check if n is non-negative
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers.")
        
        # Calculate factorial
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

    except ValueError as e:
        return f"Error: {e}"

# Test cases
print(factorial(5))     # Output: 120
print(factorial(-3))    # Output: Error: Factorial is not defined for negative numbers.
print(factorial(3.5))   # Output: Error: Input must be an integer.
print(factorial("abc")) # Output: Error: Input must be an integer.