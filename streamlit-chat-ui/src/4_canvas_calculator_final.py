# Python program to perform the sum, subtraction, multiplication, and division of two numbers


def sum_of_two_numbers(a, b):
    """Returns the sum of two numbers."""
    return a + b


def subtract_two_numbers(a, b):
    """Returns the subtraction of two numbers."""
    return a - b


def multiply_two_numbers(a, b):
    """Returns the multiplication of two numbers."""
    return a * b


def divide_two_numbers(a, b):
    """Returns the division of two numbers. Handles division by zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


# Command-line application
if __name__ == "__main__":
    # ChatGPT Link -> https://chatgpt.com/share/6790d62d-8fb0-8010-a8a3-11a2571b0a51
    while True:
        print("\nWelcome to the Calculator App")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Exit")

        choice = input("Choose an operation (1-5): ").strip()

        if choice == "5":
            print("Exiting the program. Goodbye!")
            break

        if choice in ["1", "2", "3", "4"]:
            try:
                number1 = float(input("Enter the first number: "))
                number2 = float(input("Enter the second number: "))

                if choice == "1":
                    result = sum_of_two_numbers(number1, number2)
                    print(f"The sum of {number1} and {number2} is {result}.")
                elif choice == "2":
                    result = subtract_two_numbers(number1, number2)
                    print(f"The subtraction of {number2} from {number1} is {result}.")
                elif choice == "3":
                    result = multiply_two_numbers(number1, number2)
                    print(f"The multiplication of {number1} and {number2} is {result}.")
                elif choice == "4":
                    try:
                        result = divide_two_numbers(number1, number2)
                        print(f"The division of {number1} by {number2} is {result}.")
                    except ValueError as e:
                        print(e)
            except ValueError:
                print("Invalid input! Please enter numeric values.")
        else:
            print("Invalid choice! Please select a valid option.")
