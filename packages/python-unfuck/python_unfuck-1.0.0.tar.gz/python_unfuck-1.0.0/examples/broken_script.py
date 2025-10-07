#!/usr/bin/env python3
"""
Example broken Python script for testing unfuck.
This script contains various common Python errors.
"""

# Import error - missing module
import nunpy as np  # Typo: should be numpy

# Name error - undefined variable
print(undefined_variable)

# Syntax error - missing colon
if True
    print("This will cause a syntax error")

# Type error - string concatenation
age = 25
message = "I am " + age + " years old"

# Index error
my_list = [1, 2, 3]
print(my_list[10])

# Key error
my_dict = {"name": "Alice", "age": 30}
print(my_dict["height"])

# Attribute error
my_string = "Hello"
my_string.append(" World")

# Value error
number = int("not_a_number")

# File error
with open("nonexistent_file.txt", "r") as f:
    content = f.read()

# Indentation error
def broken_function():
print("This has wrong indentation")

# Recursion error (uncomment to test)
# def infinite_recursion():
#     return infinite_recursion()
# 
# infinite_recursion()

print("If you see this, unfuck didn't work!")
