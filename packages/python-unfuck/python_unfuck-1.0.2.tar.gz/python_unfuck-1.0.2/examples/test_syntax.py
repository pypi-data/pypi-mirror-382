#!/usr/bin/env python3
"""
Test script for syntax errors.
"""

# Missing colons
if True
    print("Missing colon")

for i in range(5)
    print(i)

while True
    break

def my_function()
    return "Hello"

class MyClass()
    pass

# Assignment vs comparison
x = 5
if x = 5:  # Should be ==
    print("This is wrong")

# Unclosed brackets
my_list = [1, 2, 3
print(my_list)

# Unclosed quotes
message = "Hello world
print(message)

# Invalid indentation
def broken_function():
print("Wrong indentation")
    print("Also wrong")

print("Syntax test complete!")
