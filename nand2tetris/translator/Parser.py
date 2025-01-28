# Author: Stefan A. Law
# Date: 11/25/2023
# Description:
import os
import sys


class Parser:
    """
    Defines Parser class to be called by VMTranslator
    """

    def __init__(self, input_filename):
        """
        Takes input_filename(string) as argument
        Enumerate through file to determine line count/file length
        Open file (again) in read mode (since enumerate will move head to end of file)
        """
        path = os.getcwd() + '/' + sys.argv[1] + '/' + input_filename
        with open(path, 'r') as file:
            for count, line in enumerate(file):  # determine number of lines
                pass

        self._input_file = open(path, 'r')  # open input file to be parsed

        self._line_count = count
        self._line_index = 0

        self._current_command = ''

    def hasMoreLines(self):
        """
        determine location of file reading head in relation to length of file
        """
        if self._line_index <= self._line_count:
            return True
        else:
            self._input_file.close()
            return False

    def advance(self):
        """

        """
        self._current_command = self._input_file.readline()
        self._line_index += 1  # advance head

        if "//" in self._current_command:
            self._current_command = self._current_command[:self._current_command.find('//')]  # remove comments

        self._current_command = self._current_command.strip()  # remove whitespace

    def commandType(self):
        """

        """
        command = self._current_command.split()[0]  # lex out first part of command
        arithmetic_operators = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

        if command in arithmetic_operators:
            return 'C_ARITHMETIC'
        elif command == 'push':
            return 'C_PUSH'
        elif command == 'pop':
            return 'C_POP'
        elif command == 'label':
            return 'C_LABEL'
        elif command == 'goto':
            return 'C_GOTO'
        elif command == 'if-goto':
            return 'C_IF'
        elif command == 'function':
            return 'C_FUNCTION'
        elif command == 'return':
            return 'C_RETURN'
        elif command == 'call':
            return 'C_CALL'

    def arg1(self):
        """
        return 1st argument (string)
        """
        if self._current_command.split()[1] is None:
            return 'blank'
        else:
            return self._current_command.split()[1]

    def arg2(self):
        """
        return 2nd argument(int)
        """
        try:
            return int(self._current_command.split()[2])
        except IndexError:
            return 0

    def get_command(self):
        """
        return command
        """
        return self._current_command
