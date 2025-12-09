# your code here


import os
import sys
from modules import RAM
from modules import FileLoader
from modules import disassembler

def main():

    file_path = sys.argv[1]   # take the file path from user input

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)


    ram = RAM.simulatedRAM()        # instance of the RAM

    FileLoader.LoadtoRam(ram, file_path)


    # .text section
    print("\n.text section\n")
    disassembler.DisassembleInstructions(ram, 0x80000000, 0x80008000)

    #.data section
    print("\n.data section\n")
    disassembler.DisassembleData(ram, 0x80008000, 0x80008100)


main()

