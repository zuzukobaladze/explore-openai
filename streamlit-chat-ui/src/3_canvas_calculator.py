# Python program to perform the sum of two numbers
from dotenv import load_dotenv
load_dotenv()


def sum_of_two_numbers(a, b):
    """Returns the sum of two numbers."""
    return a + b


# Example usage
if __name__ == "__main__":
    try:
        number1 = float(input("Enter the first number: "))
        number2 = float(input("Enter the second number: "))
        result = sum_of_two_numbers(number1, number2)
        print(f"The sum of {number1} and {number2} is {result}.")
    except ValueError:
        print("Invalid input! Please enter numeric values.")
