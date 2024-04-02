"""
 @author:   Alona Skrypnyk
 @date:     04-April-2024
 @project:  Todolist
 @description:  Main functions for todolist
"""

import sqlite3
import re
import sys
from helpers import title_gen, show_menu

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
            user_id INTEGER,
            date TEXT NOT NULL,
            deadline TEXT NOT NULL,
            finished TEXT NOT NULL,
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
    if fetched_password and fetched_password[1] == password:
        is_authenticated = True
        title_gen("Todo List", 0)
        show_menu(MENUS)

        generate_menu_items()

    else:
        print('Password is incorrect')

    connection.commit()


def generate_menu_items():
    length = len(MENUS)
    choice = True

    while choice:
        try:
            user_choice = int(input("Chose the number from the menu: "))
            if user_choice in range(1, length + 1):
                if user_choice == 1:
                    view_tasks()
                elif user_choice == 2:
                    create_task()
                elif user_choice == 3:
                    update_task()
                elif user_choice == 4:
                    delete_task()
                elif user_choice == 5:
                    show_statistic()
                else:
                    sys.exit("Thank you for using our program!!!")

            else:
                print(f"Menu must be in the range 1 - {length}")

        except ValueError:
            print(f"Chose menu in the range 1 - {length}")


def view_tasks():
    print('View tasks')


def create_task():
    print('Create task')


def update_task():
    print('Update task')


def delete_task():
    print('Delete task')


def show_statistic():
    pass


def main():
    authorize()


if __name__ == "__main__":
    main()
