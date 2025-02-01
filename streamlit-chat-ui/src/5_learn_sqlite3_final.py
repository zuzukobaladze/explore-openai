"""
A simple interactive command-line to-do application using SQLite.

This version is always running and waits for user input, providing a numbered menu:
    1) Add Task
    2) Remove Task
    3) List Tasks
    4) Edit Task
    5) Mark Task Done
    6) Exit

It uses the functions defined below for each operation.
"""

import sqlite3

# The name of the SQLite database file where tasks are stored.
DB_NAME = "todos.db"


def init_db():
    """Create the tasks table if it does not exist."""
    # Connect to the SQLite database.
    # If the file doesn't exist, it will be created.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create 'tasks' table if it doesn't already exist.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Commit changes and close the connection.
    conn.commit()
    conn.close()


def add_task(title):
    """Add a new task to the database."""
    # Connect to the database.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert a new record with the specified title.
    cursor.execute("INSERT INTO tasks (title) VALUES (?)", (title,))

    # Commit the transaction and close.
    conn.commit()
    conn.close()
    print(f"Task added: '{title}'")


def list_tasks():
    """List all tasks."""
    # Connect to the database.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Select all fields from the 'tasks' table.
    cursor.execute("SELECT id, title, done, created_at FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    # If no rows, then there are no tasks.
    if not rows:
        print("No tasks found.")
        return

    # Print a header.
    print("\n--- To-Do List ---")

    # Iterate over each task row.
    for row in rows:
        task_id, title, done, created_at = row
        # Determine status based on the 'done' flag.
        status = "[X]" if done else "[ ]"
        # Display task details.
        print(f"{task_id}. {status} {title} (Created: {created_at})")


def edit_task(task_id, new_title):
    """Edit the title of an existing task."""
    # Connect to the database.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Update the 'title' field for the given 'task_id'.
    cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (new_title, task_id))
    conn.commit()

    # 'cursor.rowcount' gives the number of rows affected by the last execute.
    updated_rows = cursor.rowcount
    conn.close()

    # If at least one row was updated, display success; otherwise, show error.
    if updated_rows > 0:
        print(f"Task {task_id} updated to '{new_title}'")
    else:
        print(f"Task with ID {task_id} not found.")


def mark_done(task_id):
    """Mark a task as completed."""
    # Connect to the database.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Set 'done' to 1 for the specified task.
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()

    updated_rows = cursor.rowcount
    conn.close()

    if updated_rows > 0:
        print(f"Task {task_id} marked as done.")
    else:
        print(f"Task with ID {task_id} not found.")


def delete_task(task_id):
    """Delete a task by its ID."""
    # Connect to the database.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Delete the record with the matching 'id'.
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    deleted_rows = cursor.rowcount
    conn.close()

    if deleted_rows > 0:
        print(f"Task {task_id} deleted.")
    else:
        print(f"Task with ID {task_id} not found.")


def main():
    # Initialize (create) the database and table.
    init_db()

    # Enter a loop to continuously prompt the user.
    while True:
        print("\nSelect an option:")
        print("1) Add Task")
        print("2) Remove Task")
        print("3) List Tasks")
        print("4) Edit Task")
        print("5) Mark Task Done")
        print("6) Exit")

        # Capture user input.
        choice = input("Enter your choice: ").strip()

        # Check which option was chosen.
        if choice == '1':
            # Add a new task.
            title = input("Enter the task title: ").strip()
            add_task(title)
        elif choice == '2':
            # Remove an existing task.
            task_id = input("Enter the task ID to remove: ").strip()
            if task_id.isdigit():
                delete_task(int(task_id))
            else:
                print("Invalid task ID.")
        elif choice == '3':
            # List all tasks.
            list_tasks()
        elif choice == '4':
            # Edit an existing task.
            task_id = input("Enter the task ID to edit: ").strip()
            if task_id.isdigit():
                new_title = input("Enter the new title: ").strip()
                edit_task(int(task_id), new_title)
            else:
                print("Invalid task ID.")
        elif choice == '5':
            # Mark a task as done.
            task_id = input("Enter the task ID to mark as done: ").strip()
            if task_id.isdigit():
                mark_done(int(task_id))
            else:
                print("Invalid task ID.")
        elif choice == '6':
            # Exit the application.
            print("Exiting...")
            break
        else:
            # Invalid menu choice.
            print("Invalid choice. Please try again.")

# If this file is executed directly, run 'main()'.
if __name__ == "__main__":
    main()
