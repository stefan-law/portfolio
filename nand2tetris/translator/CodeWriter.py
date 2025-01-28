# Author: Stefan A. Law
# Date: 11/25/2023
# Description:
import sys


class CodeWriter:
    """
    See readme for documentation of assembly segments
    Has capabilites for writing arithmetic/logical commands, push/pop commands
    Has method for adding infinite loop at end of file and closing it when translation complete
    """

    def __init__(self, parser_dict, keys):
        """
        Takes input filename (string) and parser (object) as arguments
        """
        self._output_filename = sys.argv[1]
        self._parser_dict_copy = parser_dict
        if '.vm' in self._output_filename:
            self._output_filename = self._output_filename[:-3]  # create the output filename
        self._output_filename = self._output_filename + '.asm'

        self._parser_keys = keys

        self._input_filename = 'Sys'
        self._output_file = open(self._output_filename, 'w')  # create the output file and open in write mode

        self._active_parser = self._parser_dict_copy[self._parser_keys[0]]

        self._label_count = 0  # allows us to write an arbitrary number of labels and will be iterated
        self._return_label_index = 0  # allows us to write an arbitrary number of return address labels

        self._static_index = 0

        # bootstrap code
        self._output_file.write('//bootstrap code\n')
        self._output_file.write('\t@256\n')
        self._output_file.write('\tD=A\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@1\n')
        self._output_file.write('\tD=A\n')
        self._output_file.write('\tD=-D\n')
        self._output_file.write('\t@LCL\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@2\n')
        self._output_file.write('\tD=A\n')
        self._output_file.write('\tD=-D\n')
        self._output_file.write('\t@ARG\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@3\n')
        self._output_file.write('\tD=A\n')
        self._output_file.write('\tD=-D\n')
        self._output_file.write('\t@THIS\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@4\n')
        self._output_file.write('\tD=A\n')
        self._output_file.write('\tD=-D\n')
        self._output_file.write('\t@THAT\n')
        self._output_file.write('\tM=D\n')
        self.writeCall('Sys.init', 0)

    def writeArithmetic(self, operator):
        """
        Accepts operator argument (string)
        Writes arithmetic command in Hack machine language
        """
        label = str(self._label_count)
        # this may be added to commands if eq/gt/lt as these ops require label for branching

        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging

        self._output_file.write(
            "\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=M")  # common code that all ops need for getting first arg
        operations = {'add': '\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D+M',
                      'sub': '\n\tD=-D\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D+M',
                      'neg': '\n\tD=-D',
                      'eq': '\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D-M\n\t@CHECK' + label + 'TRUE\n\tD;JEQ\n\tD=-1\n(CHECK' + label + 'TRUE)\n\tD=!D\n\t@SP\n\tA=M',
                      'gt': '\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D-M\n\t@CHECK' + label + 'TRUE\n\tD;JLT\n\tD=0\n\t@CHECK' + label + 'FALSE\n\t0;JMP\n(CHECK' + label + 'TRUE)\n\tD=-1\n(CHECK' + label + 'FALSE)\n\t@SP\n\tA=M',
                      'lt': '\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D-M\n\t@CHECK' + label + 'TRUE\n\tD;JGT\n\tD=0\n\t@CHECK' + label + 'FALSE\n\t0;JMP\n(CHECK' + label + 'TRUE)\n\tD=-1\n(CHECK' + label + 'FALSE)\n\t@SP\n\tA=M',
                      'and': '\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D&M',
                      'not': '\n\tD=!D',
                      'or': '\n\t@SP\n\tM=M-1\n\t@SP\n\tA=M\n\tD=D|M'
                      }
        self._output_file.write(operations.get(operator))  # reference above dictionary to obtain needed code
        self._output_file.write('\n\tM=D\n\t@SP\n\tM=M+1\n')  # common code to store result and increment SP
        if operator == 'eq' or 'gt' or 'lt':  # increase label count for next needed label
            self._label_count += 1

    def writePushPop(self, command, segment, index):
        """
        command is C_PUSH or C_POP constant
        segment(string)
        index(int)
        Writes a push or pop command in Hack machine language
        """
        this_that = 'THIS'  # index is 0 (only relevant for this/that)
        if index == 1:
            this_that = 'THAT'

        push_segments = {'constant': '\t@' + str(index) + '\n\tD=A\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n',
                         'local': '\t@' + str(
                             index) + '\n\tD=A\n\t@LCL\n\tA=D+M\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n',
                         'argument': '\t@' + str(
                             index) + '\n\tD=A\n\t@ARG\n\tA=D+M\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n',
                         'this': '\t@' + str(
                             index) + '\n\tD=A\n\t@THIS\n\tA=D+M\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n',
                         'that': '\t@' + str(
                             index) + '\n\tD=A\n\t@THAT\n\tA=D+M\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n',
                         'temp': '\t@' + str(index + 5) + '\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1',
                         'pointer': '\t@' + this_that + '\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n',
                         'static': '\t@' + self._input_filename + '.' + str(index) + '\n\tD=M\n\t@SP\n\tA=M\n\tM=D\n\t@SP\n\tM=M+1\n'}

        pop_segments = {'local': '\t@' + str(
            index) + '\n\tD=A\n\t@LCL\n\tM=D+M\n\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@LCL\n\tA=M\n\tM=D\n\t@' + str(
            index) + '\n\tD=A\n\t@LCL\n\tM=M-D\n',
                        'argument': '\t@' + str(
                            index) + '\n\tD=A\n\t@ARG\n\tM=D+M\n\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@ARG\n\tA=M\n\tM=D\n\t@' + str(
                            index) + '\n\tD=A\n\t@ARG\n\tM=M-D\n',
                        'this': '\t@' + str(
                            index) + '\n\tD=A\n\t@THIS\n\tM=D+M\n\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@THIS\n\tA=M\n\tM=D\n\t@' + str(
                            index) + '\n\tD=A\n\t@THIS\n\tM=M-D\n',
                        'that': '\t@' + str(
                            index) + '\n\tD=A\n\t@THAT\n\tM=D+M\n\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@THAT\n\tA=M\n\tM=D\n\t@' + str(
                            index) + '\n\tD=A\n\t@THAT\n\tM=M-D\n',
                        'temp': '\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@' + str(index + 5) + '\n\tM=D\n',
                        'pointer': '\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@' + this_that + '\n\tM=D\n',
                        'static': '\t@SP\n\tM=M-1\n\tA=M\n\tD=M\n\t@' + self._input_filename + '.' + str(index) + '\n\tM=D\n'
                        }

        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging

        if command == 'C_PUSH':  # determine if push or pop and write relevant code from above dicts
            self._output_file.write(push_segments.get(segment))
        elif command == 'C_POP':
            self._output_file.write(pop_segments.get(segment))

    def writeLabel(self, label):
        """
        label (string)
        """
        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging
        self._output_file.write('(' + label + ')\n')

    def writeGoto(self, label):
        """
        label (string)
        """
        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging
        self._output_file.write('@' + label + '\n')
        self._output_file.write('0;JMP\n')

    def writeIf(self, label):
        """

        """
        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging

        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=M-1\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@' + label + '\n')
        self._output_file.write('\tD;JNE\n')

    def writeFunction(self, function_name, n_vars):
        """
        :param function_name: string
        :param n_vars: int
        :return:
        """
        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging

        # function name/label
        self._output_file.write('(' + function_name + ')\n')

        # repeat nVars times: push zero
        n_vars_count = n_vars
        while n_vars_count != 0:
            self._output_file.write('\t@SP\n')
            self._output_file.write('\tA=M\n')
            self._output_file.write('\tM=0\n')
            self._output_file.write('\t@SP\n')
            self._output_file.write('\tM=M+1\n')

            n_vars_count -= 1

    def writeCall(self, function_name, n_args):
        """
        writes code for calling a function
        takes function name and number of args (int) as parameters
        """
        if function_name == 'Sys.init':
            self._output_file.write('//call Sys.init\n')
        else:
            self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comments for debugging

        label = function_name + '$ret.' + str(self._return_label_index)  #  creates a unique label in code
        self._return_label_index += 1

        # push return address of caller function
        self._output_file.write('\t@' + label + '\n')  # point to return address
        self._output_file.write('\tD=A\n')  # store return address in D register
        self._output_file.write('\t@SP\n')  # point to stack pointer
        self._output_file.write('\tA=M\n')  # point to top of stack
        self._output_file.write('\tM=D\n')  # store return address
        self._output_file.write('\t@SP\n')  # increment stack pointer
        self._output_file.write('\tM=M+1\n')

        # push LCL of caller function
        self._output_file.write('\t@LCL\n')  # point to LCL address
        self._output_file.write('\tD=M\n')   # store LCL address in D register
        self._output_file.write('\t@SP\n')   # point to stack pointer
        self._output_file.write('\tA=M\n')   # point to top of stack
        self._output_file.write('\tM=D\n')   # push LCL address onto stack
        self._output_file.write('\t@SP\n')   # point to stack pointer
        self._output_file.write('\tM=M+1\n') # increment stack pointer

        # push ARG of caller function
        self._output_file.write('\t@ARG\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=M+1\n')

        # push THIS of caller function
        self._output_file.write('\t@THIS\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=M+1\n')

        # push THAT of caller function
        self._output_file.write('\t@THAT\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\tM=D\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=M+1\n')

        # @ARG =SP - 5 - nArgs
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@5\n')
        self._output_file.write('\tD=D-A\n')
        self._output_file.write('\t@' + str(n_args) + '\n')
        self._output_file.write('\tD=D-A\n')
        self._output_file.write('\t@ARG\n')
        self._output_file.write('\tM=D\n')

        # LCL = SP
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@LCL\n')
        self._output_file.write('\tM=D\n')

        # goto function
        self._output_file.write('\t@' + function_name + '\n')
        self._output_file.write('\t0;JEQ\n')

        # return address
        self._output_file.write('(' + label + ')\n')

    def writeReturn(self):
        """
        writes return method for a callee
        """
        self._output_file.write("// " + self._active_parser.get_command() + '\n')  # comment for debugging

        # frame (R13) = LCL
        self._output_file.write('\t@LCL\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@R13\n')
        self._output_file.write('\tM=D\n')

        # retAddr (R14) = *(frame-5)
        self._output_file.write('\t@R13\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@5\n')
        self._output_file.write('\tD=D-A\n')
        self._output_file.write('\tA=D\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@R14\n')
        self._output_file.write('\tM=D\n')

        # *ARG = pop()
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=M-1\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@ARG\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\tM=D\n')

        # SP = ARG + 1
        self._output_file.write('\t@ARG\n')
        self._output_file.write('\tD=M+1\n')
        self._output_file.write('\t@SP\n')
        self._output_file.write('\tM=D\n')

        # THAT = *(frame - 1)
        self._output_file.write('\t@R13\n')
        self._output_file.write('\tD=M-1\n')
        self._output_file.write('\tA=D\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@THAT\n')
        self._output_file.write('\tM=D\n')

        # THIS = *(frame -2)
        self._output_file.write('\t@R13\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@2\n')
        self._output_file.write('\tD=D-A\n')
        self._output_file.write('\tA=D\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@THIS\n')
        self._output_file.write('\tM=D\n')

        # ARG = *(frame-3)
        self._output_file.write('\t@R13\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@3\n')
        self._output_file.write('\tD=D-A\n')
        self._output_file.write('\tA=D\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@ARG\n')
        self._output_file.write('\tM=D\n')

        # LCL = *(frame-4)
        self._output_file.write('\t@R13\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@4\n')
        self._output_file.write('\tD=D-A\n')
        self._output_file.write('\tA=D\n')
        self._output_file.write('\tD=M\n')
        self._output_file.write('\t@LCL\n')
        self._output_file.write('\tM=D\n')

        # goto retAddr
        self._output_file.write('\t@R14\n')
        self._output_file.write('\tA=M\n')
        self._output_file.write('\t0;JMP\n')

    def setFileName(self, file_name):
        """
        file_name (string)
        Informs that the translation of a new VM file has started (called by the VMTranslator)
        """
        self._input_filename = file_name[:-3]
        self._active_parser = self._parser_dict_copy[file_name]
        self._static_index = 0

    def close(self):
        """"""
        # self.write_end_loop()  # write an infinite loop at end of code to protect memory intrusion
        self._output_file.close()  # close file

    def write_end_loop(self):
        """"""
        self._output_file.write('(END)\n')
        self._output_file.write('\t@END\n')
        self._output_file.write('\t0;JMP\n')
