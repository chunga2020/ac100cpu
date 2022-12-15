import argparse
import sys
import textwrap

import definitions as defs

parser = argparse.ArgumentParser(
    epilog=textwrap.dedent("""
    NOTE: Adjusting video dimensions changes overall VRAM allocation, which may
          lead to programs running out of general-purpose RAM during execution,
          as VRAM is dynamically allocated from general purpose RAM during
          machine initialization
    """),
    formatter_class=argparse.RawTextHelpFormatter)

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
        self.VIDEO_WIDTH: int = defs.DEFAULT_VIDEO_COLUMNS
        self.VIDEO_HEIGHT: int = defs.DEFAULT_VIDEO_ROWS
        self.VRAM_START: int = defs.DEFAULT_VRAM_START

def setup_parser(parser):
    parser.add_argument("binary", help="AC100 binary to run")
    parser.add_argument("-c", "--columns", default=defs.DEFAULT_VIDEO_COLUMNS,
                        metavar="width",
                        help="Width of emulator 'video display' (default: "
                        "%(default)s columns)")
    parser.add_argument("-d", "--debug-info", default="none",
                        help="Machine state to print for debugging purposes "
                        "(default: %(default)s)",
                        choices=["none", "registers", "ram", "flags", "all"])
    parser.add_argument("-l", "--loglevel", default="error",
                        help="Logging level (default: %(default)s)",
                        metavar="level",
                        choices=["debug", "info", "warning", "error", "critical"])
    parser.add_argument("-r", "--rows", default=defs.DEFAULT_VIDEO_ROWS,
                        metavar="height",
                        help="Height of emulator 'video display' (default: "
                        "%(default)s rows)")
