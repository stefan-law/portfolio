# Author: Stefan Law
# Date: 11/04/2024
# Description: Used by JackAnalyzer script to recursively compile
# classes from a given input file.

from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:

    def __init__(self, output_file, tokenizer):
        """
        Initialize tokenizer and associated output file

        :param: None
        :return: None
        """
        self._tokenizer = tokenizer
        self._output_file = output_file

        self._subroutines = ["constructor",
                             "function",
                             "method"]

        self._class_table = None
        self._subroutine_table = None
        self._class_name = None
        self._writer = VMWriter(tokenizer, output_file)

        self._label_index = 1

    def run_engine(self):
        """
        Loop through input file until all classes have been parsed
        and create SymbolTables. Create a new symbol table for each class
        being parsed.

        :param: None
        :return: None
        """
        while self._tokenizer.has_more_tokens():
            self._class_table = SymbolTable()
            self._subroutine_table = SymbolTable()
            self.compile_class()

    def compile_class(self):
        """
        Compiles a complete class from the input file
        Recursively calls methods for subcomponents of an input file
        """
        # Advance past opening brackets (e.g. "class Foo {" )
        self._tokenizer.advance()
        self._class_name = self._tokenizer.get_token()
        self._tokenizer.advance()
        self._tokenizer.advance()

        # Loop through each variable declaration and subroutine and write to output file until closing bracket found
        while self._tokenizer.get_token() != "}":
            if self._tokenizer.get_token() in self._subroutines:
                # reset subroutine table, then compile
                self._subroutine_table.reset()
                self.compile_subroutine(self._class_name)
            else:
                self.compile_class_var_dec()

        # Advance past closing bracket
        self._tokenizer.advance()

    def compile_class_var_dec(self):
        """Compiles a static variable declaration or a field declaration"""

        # Get kind
        kind = self._tokenizer.get_token()
        self._tokenizer.advance()

        # Get type
        type = self._tokenizer.get_token()
        self._tokenizer.advance()

        # Get name
        name = self._tokenizer.get_token()
        self._tokenizer.advance()

        # Add variable to class symbol table
        self._class_table.define(name, type, kind)

        # Check for additional declarations
        while self._tokenizer.get_token() != ";":
            if self._tokenizer.get_token() == ",":
                self._tokenizer.advance()
                continue

            name = self._tokenizer.get_token()
            self._tokenizer.advance()
            self._class_table.define(name, type, kind)

        # Advance past ending semicolon
        self._tokenizer.advance()

    def compile_subroutine(self, class_name: str):
        """Compiles a complete method, function, or constructor"""

        # Get function type
        function_type = self._tokenizer.get_token()
        self._tokenizer.advance() # point to return type

        # Get return type
        return_type = self._tokenizer.get_token()
        self._tokenizer.advance() # point to function name

        # Get function name
        function_name = f"{class_name}.{self._tokenizer.get_token()}"
        self._tokenizer.advance() # point to opening parenthesis

        # If subroutine is a method, add <this, className, arg, 0> to symbolTable mapping
        if function_type == "method":
            self._subroutine_table.define("this", class_name, "ARG")

        # Advance past opening parenthesis to parameter list
        self._tokenizer.advance()
        self.compile_parameter_list()
        self._tokenizer.advance()
        # subroutine_table now contains all params

        # Write subroutine body
        self.compile_subroutine_body(function_name, function_type, return_type)

    def compile_parameter_list(self):
        """Compiles a possibly empty parameter list"""

        # Write parameters to subroutine table
        while self._tokenizer.get_token() != ")":
            if self._tokenizer.get_token() == ",":
                self._tokenizer.advance()
            # Get type
            type = self._tokenizer.get_token()
            self._tokenizer.advance()
            # Get name
            name = self._tokenizer.get_token()
            self._tokenizer.advance()
            # Add as arg to function symbol table
            self._subroutine_table.define(name, type, "ARG")

    def compile_subroutine_body(self, function_name: str, function_type: str, return_type: str) -> None:
        """Compiles a subroutine's body"""

        # Advance past opening bracket
        self._tokenizer.advance()

        # Loop through variables and statements until closing bracket
        while self._tokenizer.get_token() == "var":
            self.compile_var_dec()

        # Calculate number of variables
        n_vars = self._subroutine_table.varCount("VAR")

        # Write the function name
        self._writer.writeFunction(function_name, n_vars)

        # If method, need to align VM THIS with base address of object
        if function_type == "method":
            self._writer.writePush("argument", 0)
            self._writer.writePop("pointer", 0)

        # housekeeping for memory allocation and segment alignment needed if constructor
        if function_type == "constructor":
            # compute memory block size (all variables are 16-bit)
            num_fields = self._class_table._counts["FIELD"]
            self._writer.writePush("constant", num_fields)
            self._writer.writeCall("Memory.alloc", 1)
            # base address of new object is now on top of stack
            # now we pop address to THIS and can write remainder of function body normally
            self._writer.writePop("pointer", 0)

        self.compile_statements(return_type)

        # Advance past closing bracket
        self._tokenizer.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration"""
        # Get kind (should be var)
        kind = self._tokenizer.get_token()
        self._tokenizer.advance()

        # Get type
        type = self._tokenizer.get_token()
        self._tokenizer.advance()

        # Get name
        name = self._tokenizer.get_token()
        self._tokenizer.advance()

        # Add var to subroutine symbol table
        self._subroutine_table.define(name, type, kind)

        # Check for additional declarations
        while self._tokenizer.get_token() != ";":
            if self._tokenizer.get_token() == ",":
                self._tokenizer.advance()
                continue

            name = self._tokenizer.get_token()
            self._tokenizer.advance()
            self._subroutine_table.define(name, type, kind)

        # Advance past ending semicolon
        self._tokenizer.advance()

    def compile_statements(self, return_type: str) -> None:
        """Compiles a sequence of statements"""

        # Loop through statements until return statements
        match self._tokenizer.get_token():
            case 'let':
                self.compile_let()
            case 'if':
                self.compile_if(return_type)
            case 'while':
                self.compile_while(return_type)
            case 'do':
                self.compile_do()
            case 'return':
                self.compile_return(return_type)
            case _:
                return

        self.compile_statements(return_type)

    def compile_let(self) -> None:
        """
        Compiles a let statement in format "let varName = expression"
        """
        # Advance past let
        self._tokenizer.advance()

        # Get varName
        varName = self._tokenizer.get_token()
        if varName in self._subroutine_table._table.keys():
            kind = self._subroutine_table._table[varName]["kind"]
            index = self._subroutine_table._table[varName]["index"]
        else:
            kind = self._class_table._table[varName]["kind"]
            index = self._class_table._table[varName]["index"]

        # Check for equals sign or bracket and advance
        self._tokenizer.advance()
        next = self._tokenizer.get_token()

        if next == "[":  # handle an array index assignment arr[i] = expr2
            self._writer.writePush(kind, index) # push arr address value to stack
            self._tokenizer.advance()
            self.compile_expression()  # determine and push arr index
            self._writer.writeArithmetic("add")
            self._tokenizer.advance()  # advance to equal
            self._tokenizer.advance()  # advance to expr2
            self.compile_expression()  # push expr2 to stack
            self._writer.writePop("temp", 0)   # pop expr2 to temp 0
            self._writer.writePop("pointer", 1) # pop arr + i address to THAT
            self._writer.writePush("temp", 0) # push expr2 to top of stack
            self._writer.writePop("that", 0)  # pop expr2 to [arr + i]
        else:
            self._tokenizer.advance() # advance to expr2
            # Get expression on stack
            self.compile_expression()

            # Pop expression to varName
            self._writer.writePop(kind, index)

        # Advance past ending semicolon
        self._tokenizer.advance()

    def compile_if(self, return_type: str):
        """Compiles an if statement"""

        # Skip "if "
        self._tokenizer.advance()

        # Write expressions following "if "
        self.compile_expression()
        # not result
        self._writer.writeArithmetic("not")

        # labels
        else_label = f"L{self._label_index}"
        self._label_index += 1
        end_label = f"L{self._label_index}"
        self._label_index += 1

        # advance past closing parenthesis and opening brace
        self._tokenizer.advance()

        self._writer.writeIf(else_label)
        # Execute if statements
        self.compile_statements(return_type)
        # advance past closing brace
        self._tokenizer.advance()
        # jump to end of if/else block
        self._writer.writeGoTo(end_label)

        # start of else block
        self._writer.writeLabel(else_label)
        if self._tokenizer.get_token() == "else":
            # Skip "else {"
            for i in range(2):
                self._tokenizer.advance()
            self.compile_statements(return_type)
            # Skip ";}"
            for i in range(1):
                self._tokenizer.advance()

        self._writer.writeLabel(end_label)

    def compile_while(self, return_type: str):
        """Compiles a while statement"""
        # labels
        start_label = f"L{self._label_index}"
        self._label_index += 1
        end_label = f"L{self._label_index}"
        self._label_index += 1

        # Skip "while"
        self._tokenizer.advance()


        # Write top label
        self._writer.writeLabel(start_label)
        # Write expression following "while" and not result
        self.compile_expression()
        self._writer.writeArithmetic("not")
        # if not, go to end
        self._writer.writeIf(end_label)
        self._tokenizer.advance()
        self.compile_statements(return_type)
        self._tokenizer.advance()
        #go to top
        self._writer.writeGoTo(start_label)
        #END
        self._writer.writeLabel(end_label)

    def compile_do(self) -> None:
        """Compiles a do statement"""
        # Skip do
        self._tokenizer.advance()

        # Determine if subroutine_name(expression_list) or class_name.subroutine_name syntax
        current = self._tokenizer.get_token()
        self._tokenizer.advance()
        next = self._tokenizer.get_token()

        # Handle class_name.subroutine call
        if next == ".":
            class_name = current
            n_args = 0
            if class_name in self._subroutine_table._table.keys():
                segment = self._subroutine_table._table[class_name]["kind"]
                index = self._subroutine_table._table[class_name]["index"]
                class_name = self._subroutine_table._table[class_name]["type"]
                self._writer.writePush(segment, index)
                n_args += 1
            elif class_name in self._class_table._table.keys():
                segment = self._class_table._table[class_name]["kind"]
                index = self._class_table._table[class_name]["index"]
                class_name = self._class_table._table[class_name]["type"]
                self._writer.writePush(segment, index)
                n_args += 1
            self._tokenizer.advance()
            subroutine = self._tokenizer.get_token()
            self._tokenizer.advance()  # advance past opening parenthesis
            self._tokenizer.advance()
            n_args += self.compile_expression_list()
            self._writer.writeCall(f"{class_name}.{subroutine}", n_args)
        # Handle subroutine_name(expression_list)
        else:
            # We are effectively saying "this.method_name(args)"
            # So, push this
            self._writer.writePush("pointer", 0)
            subroutine_name = current
            self._tokenizer.advance()  # advance past opening parenthesis
            n_args = self.compile_expression_list()
            self._writer.writeCall(f"{self._class_name}.{subroutine_name}", n_args + 1)

        # Advance past ending ") and semicolon"
        for i in range(2):
            self._tokenizer.advance()

        # Store resulting topmost stack value in temp 0
        self._writer.writePop("temp", 0)

    def compile_return(self, return_type: str):
        """Compiles a return statement"""
        # Write expression if present
        self._tokenizer.advance()
        if self._tokenizer.get_token() != ';':
            if self._tokenizer.get_token() == '(':
                self._tokenizer.advance()
                self.compile_expression_list()
            else:
                self.compile_expression()
        self._tokenizer.advance() # advance past terminating semicolon

        # If void return type, push zero on the stack
        if return_type == "void":
            self._writer.writePush("constant", 0)

        # Write return command
        self._writer.writeReturn()

    def compile_expression(self) -> None:
        """Compiles an expression"""

        expression_terminators = [',', ')', ';', '}', '{', ']']
        unary_op = {'-': "neg", '~': "not"}
        binary_op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        keyword_const = ["null", "false", "true", "this"]
        unary_flag = 1
        type = None

        # Write expression (multiple terms) in postfix using expression list
        while self._tokenizer.get_token() not in expression_terminators:
            current_token = self._tokenizer.get_token()

            # An additional open parenthesis denotes another expression
            if current_token == '(':
                self._tokenizer.advance()
                self.compile_expression()
                if self._tokenizer.get_token() == ')':
                    self._tokenizer.advance()  # pass closing parenthesis

            # Check for unary ops
            elif unary_flag == 1 and current_token in unary_op:
                op = current_token
                self._tokenizer.advance()
                self.compile_expression() # push expr following op
                self.compile_term("unary", op)

            # Check for regular ops
            elif current_token in binary_op:
                op = current_token
                self._tokenizer.advance()
                self.compile_expression() # push expr following op
                self.compile_term("op", op)

            # Check for numeric constant
            elif current_token.isnumeric():
                self.compile_term("integerConstant", current_token)
                self._tokenizer.advance()

            # Check for keyword constant
            elif current_token in keyword_const:
                self.compile_term("keywordConstant", current_token)
                self._tokenizer.advance()

            # Check for string
            elif current_token[0] == '\'' or current_token[0] == '\"':
                # Calculate and push input string length to stack
                string_length = len(current_token) - 2
                self._writer.writePush("constant", string_length)
                # Call string constructor
                self._writer.writeCall("String.new", 1)
                # Push the character code for each character in the string onto the stack,
                # and then call appendChar
                for char in current_token[1:-1]:
                    self._writer.writePush("constant", ord(char))
                    self._writer.writeCall("String.appendChar", 2)

                self._tokenizer.advance()

            # Check for variables or array access
            elif current_token in self._subroutine_table._table or current_token in self._class_table._table:
                # We retain segment and index in case we have var.method() call
                type = self.compile_term("varName", current_token)  # push array name or variable name
                self._tokenizer.advance()

            elif self._tokenizer.get_token() == "[":
                self._tokenizer.advance()  # advance past opening bracket
                self.compile_expression()  # determine and push arr index
                self.compile_term("array")
                if self._tokenizer.get_token() == ']':
                    self._tokenizer.advance()  # advance past closing bracket

            # Check for method that is related to a variable call
            elif self._tokenizer.get_token() == '.':
                self._tokenizer.advance()
                function_name = self._tokenizer.get_token()
                self._tokenizer.advance()  # advance to opening parenthesis
                self._tokenizer.advance()  # advance to args
                n_args = self.compile_expression_list()
                self._tokenizer.advance()  # advance past closing parenthesis
                self._writer.writeCall(f"{type}.{function_name}", n_args + 1)

            # Must be a function call
            else:
                self._tokenizer.advance()
                # Check if "class.function(args)" or just "function(args)"
                if self._tokenizer.get_token() == '.':
                    class_name = current_token
                    if class_name in self._subroutine_table._table.keys():
                        segment = self._subroutine_table._table[class_name]["kind"]
                        index = self._subroutine_table._table[class_name]["index"]
                        type = self._subroutine_table._table[class_name]["type"]
                        self._writer.writePush(segment, index)
                    elif class_name in self._class_table._table.keys():
                        segment = self._class_table._table[class_name]["kind"]
                        index = self._class_table._table[class_name]["index"]
                        type = self._subroutine_table._table[class_name]["type"]
                        self._writer.writePush(segment, index)
                    else:
                        type = class_name

                    self._tokenizer.advance()
                    function_name = self._tokenizer.get_token()
                    self._tokenizer.advance()
                    self._tokenizer.advance()
                    n_args = self.compile_expression_list()  # compile args
                    self._tokenizer.advance()
                    self._writer.writeCall(f"{type}.{function_name}", n_args)
                else:
                    # We are effectively saying "this.method_name(args)"
                    # So, push this
                    self._writer.writePush("pointer", 0)
                    # Get our function name and advance to args
                    function_name = current_token
                    self._tokenizer.advance()
                    self._tokenizer.advance()
                    # Compile args
                    n_args = self.compile_expression_list()
                    self._tokenizer.advance()
                    self._writer.writeCall(f"{function_name}", n_args + 1)


            # If not at beginning of loop for current expression, can't be unary
            unary_flag = 0

    def compile_term(self, term_type: str, term=None) -> None | str:
        """Compiles a term"""
        keyword_const = {"null": {"segment": "constant", "index": 0}, "false": {"segment": "constant", "index": 0},
                         "true": {"segment": "constant", "index": 1}, "this": {"segment": "pointer", "index": 0}}

        if term_type == "integerConstant":
            self._writer.writePush("constant", int(term))
        elif term_type == "keywordConstant":
            self._writer.writePush(keyword_const[term]["segment"], keyword_const[term]["index"])
            if term == "true":
                self._writer.writeArithmetic('neg')
        elif term_type == "array":
            # add arr index to arr address
            self._writer.writeArithmetic("add")
            # pop effective address to THAT (pointer 1)
            self._writer.writePop("pointer", 1)
            # access data at address
            self._writer.writePush("that", 0)
        elif term_type == "unary":
            command = "neg" if term == "-" else "not"
            self._writer.writeArithmetic(command)
        elif term_type == "op":
            match term:
                case "+":
                    self._writer.writeArithmetic("add")
                case "-":
                    self._writer.writeArithmetic("sub")
                case "*":
                    self._writer.writeCall("Math.multiply", 2)
                case "/":
                    self._writer.writeCall("Math.divide", 2)
                case "&":
                    self._writer.writeArithmetic("and")
                case "|":
                    self._writer.writeArithmetic("or")
                case "<":
                    self._writer.writeArithmetic("lt")
                case ">":
                    self._writer.writeArithmetic("gt")
                case "=":
                    self._writer.writeArithmetic("eq")
                case _:
                    pass
        else: #  variable
            if term in self._subroutine_table._table.keys():
                segment = self._subroutine_table._table[term]["kind"]
                index = self._subroutine_table._table[term]["index"]
                type = self._subroutine_table._table[term]["type"]
            elif term in self._class_table._table.keys():
                segment = self._class_table._table[term]["kind"]
                index = self._class_table._table[term]["index"]
                type = self._class_table._table[term]["type"]

            self._writer.writePush(segment, index)
            # Return segment and index of variable in case it's an object method call
            return type

    def compile_expression_list(self) -> int:
        """
        Compiles a comma separated list of expressions
        Returns integer of expressions in list

        param: None
        return: integer # of expressions in expression list
        """
        num_expressions = 0
        expression_terminators = [')', ';']

        # Loop through arguments
        while self._tokenizer.get_token() not in expression_terminators:
            if self._tokenizer.get_token() == ",":
                self._tokenizer.advance()
            else:
                self.compile_expression()
                num_expressions += 1

        return num_expressions
