# Author: Stefan Law
# Date: 11/04/2024
# Description: Creates a symbol table for class or method/function level
# tabulation of symbols and whether they have been encountered before or not.
# The symbol values are also enumerated for the stack that they belong to.

class SymbolTable:
    """
    Provides services for building,populating, and using symbol tables that
    keep track of the symbol properties name, type, kind, and a running index
    for each kind.
    """

    def __init__(self):
        self._table = {}
        self._counts = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def reset(self) -> None:
        """
        Empties the symbol table and resets count indices to zero.
        Should be called when starting a subroutine declaration.

        :param: None
        :return: None
        """
        self._table = {}
        self._counts = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def define(self, name: str, type: str, kind: str) -> None:
        """
        Adds a new variable with given name/type/kind to SymbolTable. Assigns
        it to the index value of that kind and increments index.
        :param name: string name of the variable being defined
        :param type: string type of the variable being defined
        :param kind: string kind of the variable being defined
        :return: None
        """
        self._table[name] = {"type": type, "kind": kind, "index": self._counts[kind.upper()]}
        self._counts[kind.upper()] += 1

    def varCount(self, kind: str) -> int:
        """
        Returns the number of variables of the given kind already defined in the table

        :param kind:
        :return:
        """
        return self._counts[kind]

    def kindOf(self, name: str) -> str | None:
        """
        Returns the kind of the named identifier (STATIC, FIELD, ARG, VAR or NONE).
        NONE is returned if the identifier is not found.
        :param name: the string name of thee variable being referenced
        :return:
        """
        if name in self._table.keys():
            return self._table[name]["kind"]

        return None

    def typeOf(self, name: str) -> str:
        """
        Returns the type of the named variable

        :param name: the string name of the variable being referenced
        :return: string
        """
        return self._table[name]["type"]

    def indexOf(self, name: str) -> int:
        """
        Returns the index of the named variable
        :param name: the string name of the variable being referenced
        :return: int
        """
        return self._table[name]["index"]




