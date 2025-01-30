import sqlite3
from dotenv import load_dotenv
load_dotenv()


# Function to create the tasks table if it doesn't already exist
def create_table():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        task TEXT,
                        status TEXT)""")
    conn.commit()
    conn.close()


# Function to add a new task to the database
def add_task(task):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task, status) VALUES (?, ?)", (task, "pending"))
    conn.commit()
    conn.close()


# Function to retrieve all tasks from the database
def list_tasks():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Function to mark a task as completed based on its ID
def complete_task(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", ("completed", task_id))
    conn.commit()
    conn.close()


# Main function to run the command-line to-do list app
def main():
    create_table()  # Ensure the table exists

    while True:
        # Display the main menu
        print("\nTo-Do List App")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Complete Task")
        print("4. Exit")

        # Prompt the user for a choice
        choice = input("Enter your choice: ")

        if choice == "1":
            # Add a new task
            task = input("Enter the task: ")
            add_task(task)
            print("Task added successfully!")
        elif choice == "2":
            # List all tasks
            tasks = list_tasks()
            print("\nTasks:")
            for task in tasks:
                print(f"ID: {task[0]}, Task: {task[1]}, Status: {task[2]}")
        elif choice == "3":
            # Mark a task as completed
            task_id = input("Enter the task ID to mark as completed: ")
            complete_task(int(task_id))
            print("Task marked as completed!")
        elif choice == "4":
            # Exit the app
            print("Exiting the app. Goodbye!")
            break
        else:
            # Handle invalid input
            print("Invalid choice. Please try again.")


# Entry point for the application
if __name__ == "__main__":
    main()
    # Chatgpt Link
    # https://chatgpt.com/share/678faa51-a088-8010-87b7-0e227b06c923
