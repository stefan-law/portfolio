# Author: Stefan Law
# Date: 11/04/2024
# Description: Defines a main() procedure that coordinates the activities
# of a tokenizer and compilation engine for interpreting the Jack
# language from "Nand2Tetris"

import os
import sys
import compilationEngine
import tokenizer


def main():
    """
    Collect filename to be analyzed from CLI
    Initializes and invokes tokenizer and compilation engine
    Creates output files to be written to
    Runs tokenizer and compilation engine for each file, then closes output files

    param: None
    :return: None
    """
    input_filename = sys.argv[1]
    tokenizer_list = []
    path = os.getcwd() + '/' + input_filename

    # Setup for single vs multiple input files
    if ".jack" in input_filename:
        output_filename = input_filename[:input_filename.find(".jack")] + ".vm"
        output_file = open(output_filename, 'w')
        tokenizer_list.append((tokenizer.Tokenizer(path), output_file))
    else:
        for filename in os.listdir(path):
            if ".jack" in filename:
                output_filename = filename[:filename.find(".jack")] + ".vm"
                output_file = open(output_filename, 'w')
                tokenizer_list.append((tokenizer.Tokenizer(path + '/' + filename), output_file))
    # Iterate through tokenization procedure for each input file
    for reader in tokenizer_list:
        tokens = reader[0]
        file = reader[1]
        engine = compilationEngine.CompilationEngine(file, tokens)
        tokens.advance()
        engine.run_engine()
        file.close()


if __name__ == "__main__":
    main()
