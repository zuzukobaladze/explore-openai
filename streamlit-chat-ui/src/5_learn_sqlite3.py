import sqlite3


def create_table():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        task TEXT,
                        status TEXT)""")
    conn.commit()
    conn.close()


def add_task(task):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task, status) VALUES (?, ?)", (task, "pending"))
    conn.commit()
    conn.close()


def list_tasks():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows


def complete_task(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", ("completed", task_id))
    conn.commit()
    conn.close()


def main():
    create_table()
    while True:
        print("\nTo-Do List App")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Complete Task")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            task = input("Enter the task: ")
            add_task(task)
            print("Task added successfully!")
        elif choice == "2":
            tasks = list_tasks()
            print("\nTasks:")
            for task in tasks:
                print(f"ID: {task[0]}, Task: {task[1]}, Status: {task[2]}")
        elif choice == "3":
            task_id = input("Enter the task ID to mark as completed: ")
            complete_task(int(task_id))
            print("Task marked as completed!")
        elif choice == "4":
            print("Exiting the app. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
