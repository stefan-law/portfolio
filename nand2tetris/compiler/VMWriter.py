# Author: Stefan Law
# Date: 11/04/2024
# Description: Used by compilationEngine script to write individual lines of
# VM code in Jack language

from __future__ import annotations
from tokenizer import Tokenizer

import typing
class VMWriter:

    def __init__(self, tokenizer: Tokenizer, output_file: typing.TextIO):
        """"""
        self._tokenizer = tokenizer
        self._output_file = output_file

    def writePush(self, segment: str, index: int) -> None:
        """

        :param segment:
        :param index:
        :return:
        """
        match segment.upper():
            case "STATIC":
                segment = "static"
            case "FIELD":
                segment = "this"
            case "ARG":
                segment = "argument"
            case "VAR":
                segment = "local"
            case _:
                pass

        self._output_file.write(f"push {segment} {index}\n")

    def writePop(self, segment: str, index: int) -> None:
        """

        :param segment:
        :param index:
        :return:
        """
        match segment.upper():
            case "STATIC":
                segment = "static"
            case "FIELD":
                segment = "this"
            case "ARG":
                segment = "argument"
            case "VAR":
                segment = "local"
            case _:
                pass

        self._output_file.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, command: str) -> None:
        """

        :param command:
        :return:
        """
        self._output_file.write(f"{command.lower()}\n")

    def writeLabel(self, label: str) -> None:
        """

        :param label:
        :return:
        """
        self._output_file.write(f"label {label}\n")

    def writeGoTo(self, label: str) -> None:
        """

        :param label:
        :return:
        """
        self._output_file.write(f"goto {label}\n")

    def writeIf(self, label: str) -> None:
        """

        :param label:
        :return:
        """
        self._output_file.write(f"if-goto {label}\n")

    def writeCall(self, name: str, n_args: int) -> None:
        """

        :param name:
        :param n_args:
        :return:
        """
        self._output_file.write(f"call {name} {n_args}\n")

    def writeFunction(self, name: str, n_vars: int) -> None:
        """

        :param name:
        :param n_vars: number of local variables in subroutine
        :return:
        """
        self._output_file.write(f"function {name} {n_vars}\n")

    def writeReturn(self) -> None:
        """

        :return:
        """
        self._output_file.write(f"return\n")
