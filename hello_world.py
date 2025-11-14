import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "Local Development")

def greet():
    print(f"Hello from {ENVIRONMENT}!")

if __name__ == "__main__":
    greet()
