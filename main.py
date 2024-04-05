"""
 @author:   Alona Skrypnyk
 @date:     04-April-2024
 @project:  Todolist
 @description:  Main functions for todolist
"""
import datetime
import sqlite3
import re
import sys
from helpers import title_gen, show_menu
from tabulate import tabulate

is_authenticated = False
MENUS = ["View Tasks", "Add Task", "Set Is Done", "Remove Task", "Show Statistic", "Logout"]


def initialize_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Create the users table
    create_users_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    '''
    cursor.execute(create_users_table_query)

    # Create the tasks table
    create_tasks_table_query = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            user_id INTEGER,
            date TEXT NOT NULL,
            deadline TEXT NOT NULL,
            finished TEXT,
            is_done INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    '''
    cursor.execute(create_tasks_table_query)

    # Commit the changes and close the connection
    connection.commit()
    connection.close()


initialize_db()


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
        print(result)

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
    print(fetched_password)
    if fetched_password and fetched_password[1] == password:
        is_authenticated = True
        title_gen("Todo List", 0)
        show_menu(MENUS)
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


def generate_menu_items(user_id=1):
    length = len(MENUS)
    choice = True

    while choice:
        try:
            user_choice = int(input("Chose the number from the menu: "))
            if user_choice in range(1, length + 1):
                if user_choice == 1:
                    view_tasks(user_id)
                    show_menu(MENUS)
                elif user_choice == 2:
                    create_task(user_id)
                    show_menu(MENUS)
                elif user_choice == 3:
                    update_task(user_id)
                    show_menu(MENUS)
                elif user_choice == 4:
                    delete_task()
                    show_menu(MENUS)
                elif user_choice == 5:
                    show_statistic()
                    show_menu(MENUS)
                else:
                    sys.exit("Thank you for using our program!!!")

        except ValueError:
            raise ValueError(f"Chose menu in the range 1 - {length}")
        except KeyboardInterrupt:
            sys.exit("Bye, Bye")


def view_tasks(user_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    get_tasks = f"SELECT * FROM tasks WHERE user_id == '{user_id}'"
    cursor.execute(get_tasks)
    tasks = cursor.fetchall()
    data = []
    for el in tasks:
        data.append(list(el))
    clean_data = [["Task number", "Title", "Deadline", "Status"]]
    for i in data:
        n = [i[0], i[1], i[4], "Finished" if i[6] == 1 else "In Process"]
        clean_data.append(n)
    print(tabulate(clean_data, tablefmt="grid"))
    cursor.close()


def check_deadline(data):
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


def create_task(user_id):
    deadline = get_deadline()
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    title = get_title()

    data = (user_id, title, datetime.datetime.now(), deadline, 0)
    cursor.execute("INSERT INTO tasks (user_id, title, date, deadline, is_done) VALUES (?, ?, ?, ?, ?)", data)
    connection.commit()
    connection.close()


def update_task(user_id):
    print('Update task')
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    get_tasks = f"SELECT * FROM tasks WHERE user_id == '{user_id}'"
    cursor.execute(get_tasks)
    tasks = cursor.fetchall()
    view_tasks(user_id)
    task_id = get_number_in_interval(1, len(tasks))
    change_status = f"UPDATE tasks SET is_done = ?, finished= ? WHERE user_id = ? AND id = ?"
    cursor.execute(change_status, (1, datetime.datetime.now().date(), user_id, task_id))
    print("Status is changed")

    connection.commit()


def delete_task():
    print('Delete task')


def show_statistic():
    pass


def main():
    show_menu(MENUS)
    generate_menu_items(1)


if __name__ == "__main__":
    main()
