import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "Local Development")

def greet():
    print(f"Hello from {ENVIRONMENT}!")
    print("I AM LOCKED IN FULL OF EXCITEMENT AND COOLNESS OH YEAH")

if __name__ == "__main__":
    greet()
