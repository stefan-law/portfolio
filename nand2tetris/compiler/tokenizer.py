# Author: Stefan Law
# Date: 11/04/2024
# Description: Takes an input Jack source file and tokenizes it for interpretation and compilation by
# the Jack VM compiler

class Tokenizer:
    """"""

    def __init__(self, input_filename: str) -> None:
        """"""
        self._path = input_filename
        self._file = open(self._path, 'r')
        self._char = self._file.read(1)
        self._buffer = ""

        self._keyword_table = [
            'class',
            'constructor',
            'function',
            'method',
            'field',
            'static',
            'var',
            'int',
            'char',
            'boolean',
            'void',
            'true',
            'false',
            'null',
            'this',
            'let',
            'do',
            'if',
            'else',
            'while',
            'return'
        ]

        self._whitespace_table = [
            " ",
            "\t",
            "\n"
        ]

        self._symbol_table = [
            '{',
            '}',
            '(',
            ')',
            '[',
            ']',
            '.',
            ',',
            ';',
            '+',
            '-',
            '*',
            '/',
            '&',
            '|',
            '<',
            '>',
            '=',
            '~'
        ]

    def get_token(self) -> str:

        match self.token_type():
            case 'KEYWORD':
                return self.keyword()
            case 'SYMBOL':
                return self.symbol()
            case 'IDENTIFIER':
                return self.identifier()
            case 'INT_CONST':
                return str(self.int_val())
            case 'STRING_CONST':
                return self.string_val()
            case _:
                return 'ERROR'

    def has_more_tokens(self) -> bool:
        """"""

        if self._buffer == '':
            return False

        return True

    def advance(self) -> None:
        """
        Advances file to next token
        Removes comments
        :return:
        """
        self._buffer = ""

        # Get rid of white space
        while self._char in self._whitespace_table:
            self._char = self._file.read(1)

        # Check for comments and skip
        if self._char == "/":
            if self.check_comment():
                return self.advance()

        # Check for a string
        if self._char == "\"":
            self._buffer += self._char
            self._char = self._file.read(1)
            while self._char != "\"":
                self._buffer += self._char
                self._char = self._file.read(1)
            self._buffer += self._char
            self._char = self._file.read(1)
            return

        # Check for a symbol
        if self._char in self._symbol_table:
            self._buffer = self._char
            self._char = self._file.read(1)
            return

        # Build buffer until whitespace or symbol encountered (or EOF)
        while self._char not in self._symbol_table and self._char not in self._whitespace_table:
            self._buffer += self._char
            self._char = self._file.read(1)
            if self._char == '':
                break

    def check_comment(self) -> bool:
        """"""

        check = self._file.read(1)
        match check:
            case '/':
                while self._file.read(1) != "\n":
                    continue
                self._char = self._file.read(1)
                return True
            case '*':

                temp = self._file.read(1)
                check = self._file.read(1)
                while temp != '*' or check != '/':
                    temp = check
                    check = self._file.read(1)
                self._char = self._file.read(1)
                return True
            case _:
                self._char = '/'
                return False

    def token_type(self) -> str:
        """"""

        # Check if first character of token is a symbol
        if self._buffer in self._symbol_table:
            return 'SYMBOL'
        # If not symbol, check if token is an integerConstant (isDigit())
        elif self._buffer[0].isdigit():
            return 'INT_CONST'
        # Check if first character is ", meaning token is a string
        elif self._buffer[0] == '"':
            return 'STRING_CONST'
        # Check if token is a keyword
        elif self._buffer in self._keyword_table:
            return 'KEYWORD'
        # Since token is none of the above, it must be an identifier

        return 'IDENTIFIER'

    def keyword(self) -> str:
        """"""

        return self._buffer

    def symbol(self) -> str:
        """"""

        return self._buffer

    def identifier(self) -> str:
        """"""
        return self._buffer

    def int_val(self) -> int:
        """"""

        return int(self._buffer)

    def string_val(self) -> str:
        """"""
        
        return self._buffer
