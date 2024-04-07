"""
 @author:   Alona Skrypnyk
 @date:     04-April-2024
 @project:  Todolist
 @description:  Main functions for todolist
"""
import datetime
import os
import sqlite3
import re
import sys
from helpers import title_gen, show_menu
from tabulate import tabulate

is_authenticated = False
MENUS = ["View Tasks", "Add Task", "Set Is Done", "Remove Task", "Show Statistic", "Logout"]


def initialize_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                user_id INTEGER,
                date TEXT NOT NULL,
                deadline TEXT NOT NULL,
                finished TEXT,
                is_done INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')


def execute_db(query, params=(), fetch=False):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()


def fetch_and_display_tasks(user_id):
    clear_screen()
    tasks = execute_db("SELECT * FROM tasks WHERE user_id = ?", (user_id,), fetch=True)
    if not tasks:
        print("No tasks found for this user.")
        return tasks

    headers = ["Task number", "Title", "Deadline", "Status"]
    clean_data = [headers] + [[index + 1, task[1], task[4], "Finished" if task[6] == 1 else "In Process"]
                              for index, task in enumerate(tasks)]
    title_gen("Todo List", 0)
    print(tabulate(clean_data, tablefmt="grid"))
    return tasks


def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.[\w-]+$"
    return re.match(pattern, email) is not None


def validate_password(password):
    pattern = r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d\W_]+$'
    return re.search(pattern, password) is not None


def password_checker(password):
    leng = len(password)
    if leng < 8:
        print("Password is too short, try another one")
    elif not validate_password(password):
        print("Password must have at least one number and any character")
    else:
        return True


def email_checker(email):
    if not validate_email(email):
        print("You input email is in incorrect format")
    else:
        return True


class Validate:
    @staticmethod
    def email(authorized=False):
        email = input("Your Email: ").strip()
        if email_checker(email):
            return email

    @staticmethod
    def password(authorized=False):
        extra_message = " (Must contain at least 8 chars and contain character, number and letter in it)"
        password = input(f"Your Password{'' if authorized else extra_message}: ").strip()
        if password_checker(password):
            return password


def validate_field(field, authorized):
    check = Validate()
    invalid = True
    while invalid:
        method = getattr(check, field)
        current_field = method(authorized)
        if current_field:
            return current_field


def authorize():
    # Connect to the database
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    mail = validate_field('email', False)
    if mail:
        # Execute a SELECT query
        user = f"SELECT * FROM users WHERE email = '{mail}'"

        cursor.execute(user)
        result = cursor.fetchall()

        if result:
            print("We find you in our system")
            password = validate_field('password', True)
            if password:
                login(mail, password)
        else:
            answer = input("Sorry we dont find your email in our database. Do you like to register? Y/N ")
            if answer[0].lower() == "y":
                add_user(mail)
            elif answer[0].lower() == "n":
                sys.exit("Bye. Thank you for choosing our app!!!")

        connection.close()


def add_user(email):
    print(f"I am not in the System. But I want to become user")
    password = validate_field('password', False)
    if password:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        insert_user_query = f"INSERT INTO users (password, email) VALUES ('{password}', '{email}')"

        # Execute the INSERT query
        cursor.execute(insert_user_query)

        # Commit the transaction to save the changes
        connection.commit()
        print("New account been created. Redirecting to main menu")
        login(email, password)


def login(email, password):
    global is_authenticated

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    authorize_pass = f"SELECT id, password FROM users WHERE email == '{email}'"
    cursor.execute(authorize_pass)
    fetched_password = cursor.fetchone()
    if fetched_password and fetched_password[1] == password:
        is_authenticated = True
        clear_screen()
        title_gen("Todo List", 0)
        generate_menu_items(fetched_password[0])
    else:
        print('Password is incorrect')

    connection.commit()


def get_number_in_interval(min_val, max_val):
    while True:
        try:
            number = float(input(f"Enter a number between {min_val} and {max_val}: "))
            if min_val <= number <= max_val:
                return number
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('\n' * 70)


def check_deadline(data):
    clear_screen()
    no_input = True
    while no_input:
        try:
            format_string = "%Y-%m-%d"
            user_date = datetime.datetime.strptime(data, format_string).date()
            return user_date
        except ValueError:
            print("Invalid date format. Please enter a date in the format YYYY-MM-DD.")
            data = input("Enter a valid date YYYY-MM-DD: ")


def get_deadline():
    deadline = input("Enter the date of Deadline (YYYY-MM-DD): ")
    return check_deadline(deadline)


def get_title():
    invalid = True
    while invalid:
        title = input("Add task title: ").strip()
        if len(title) > 1:
            return title
        else:
            print("Title can't be empty")
            return get_title()


def generate_menu_items(user_id=1):
    while True:
        show_menu(MENUS)
        try:
            user_choice = int(input("Choose the number from the menu: "))
            if 1 <= user_choice <= len(MENUS):
                if user_choice == 1:
                    title_gen("Todo List", 0)
                    fetch_and_display_tasks(user_id)
                elif user_choice == 2:
                    create_task(user_id)
                elif user_choice == 3:
                    update_task(user_id)
                elif user_choice == 4:
                    delete_task(user_id)
                elif user_choice == 5:
                    show_statistic(user_id)
                elif user_choice == 6:
                    print("Thank you for using our program!!!")
                    break
            else:
                print(f"Please choose a number in the range 1 - {len(MENUS)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def create_task(user_id):
    clear_screen()
    title_gen("Todo List", 0)
    title = get_title()
    deadline = get_deadline()
    execute_db("INSERT INTO tasks (user_id, title, date, deadline, is_done) VALUES (?, ?, ?, ?, ?)",
               (user_id, title, datetime.datetime.now().date(), deadline, 0))


def update_task(user_id):
    clear_screen()
    title_gen("Todo List", 0)
    tasks = fetch_and_display_tasks(user_id)
    if tasks:
        task_number = int(get_number_in_interval(1, len(tasks)))
        task_id = tasks[task_number - 1][0]
        execute_db("UPDATE tasks SET is_done = not is_done, finished = ? WHERE user_id = ? AND id = ?",
                   (datetime.datetime.now().date(), user_id, task_id))


def delete_task(user_id):
    clear_screen()
    title_gen("Todo List", 0)
    tasks = fetch_and_display_tasks(user_id)
    if tasks:
        task_number = int(get_number_in_interval(1, len(tasks)))
        task_id = tasks[task_number - 1][0]
        execute_db("DELETE FROM tasks WHERE user_id = ? AND id = ?", (user_id, task_id))


def get_timedelta(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def show_statistic(user_id):
    clear_screen()
    title_gen("Todo List", 0)
    tasks = execute_db("SELECT * FROM tasks WHERE user_id = ?", (user_id,), fetch=True)
    if not tasks:
        print("No tasks found for this user.")
        return tasks
    current_date = datetime.datetime.now().date()

    statistic = {
        "in_progress": 0,
        "finished":    0,
        "expired":     0,
        "overdue":     0
    }
    items = [task for task in tasks]
    for i in items:
        if i[5] is None:
            if current_date < get_timedelta(i[4]):
                statistic["in_progress"] += 1
            elif current_date > get_timedelta(i[4]):
                statistic["expired"] += 1
        elif get_timedelta(i[5]) > get_timedelta(i[4]):
            statistic["overdue"] += 1
        else:
            statistic["finished"] += 1

    elements = [list(statistic.keys()), list(statistic.values())]
    print(tabulate(elements, tablefmt="grid"))


def main():
    clear_screen()
    authorize()
    # # show_menu(MENUS)
    # generate_menu_items(1)


if __name__ == "__main__":
    main()
