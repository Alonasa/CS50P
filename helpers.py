"""
 @author:   Alona Skrypnyk
 @date:     04-April-2024
 @project:  Todolist
 @description:  Helper functions for todolist
"""


def title_gen(title, expired, helper='*'):
    """
    (string, string, int) -> None
    Generate pretty game title, according to arguments passing by user
    """
    length = 75
    line = length * helper
    exp = ''
    length_last = len(str(expired)) + 1
    if expired > 0:
        exp = f"\n{'Expired: ': >{length - length_last}}{expired}"

    print(f"{line}\n\n{title.title(): ^{length}}{exp}\n\n{line}\n")


def show_menu(items):
    """
    (list of str) -> None
    Generate numerated menu from a list of strings
    """
    for index, item in enumerate(items):
        print(f"{index + 1}) {item}")
