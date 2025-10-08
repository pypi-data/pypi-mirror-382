#!/usr/bin/env python3
import sys

print("Hello World!")
print("Testing output...")
sys.stdout.flush()

def test():
    print("Inside function")
    return True

if __name__ == "__main__":
    print("Starting...")
    result = test()
    print(f"Result: {result}")
    print("Done!")

