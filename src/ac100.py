import argparse
import sys

import src.definitions as defs

# AC100 emulator
class AC100:

    REGS: bytearray
    RAM: bytearray
    PS: int                     # status register
    SP: int                     # stack pointer

    def __init__(self):
        self.REGS = [[0x00 for i in range(defs.BYTES_PER_WORD)]\
                     for j in range(defs.NUM_REGISTERS)]
        self.RAM = bytearray(defs.ADDRESS_SIZE)
        self.PS = 0x00          # 0b00000000
        self.SP = defs.STACK_MIN
