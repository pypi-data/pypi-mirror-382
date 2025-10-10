"""
This code here has some functions that we will call in our tests.
"""

import os.path as path


def add(a: int, b: int) -> int:
    """
    A simple function for adding 2 numbers

    :param a: first term
    :param b: second term
    :return: sum
    """
    return a + b

def error() -> None:
    """
    Raises an error for testing purposes
    """
    raise Exception("HELP THIS IS AN ERROR")

def openFile() -> str:
    """
    Opens the file 'afile.txt'

    :return: file text
    """
    with open(path.dirname(__file__) + '/afile.txt') as f:
        return f.read().strip('\n')

def printTable() -> None:
    """
    Uses the tabulate module to print a table
    """
    import tabulate as t
    print(t.tabulate([[1,2,3]], ['a', 'b', 'c']))