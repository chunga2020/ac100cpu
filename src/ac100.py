import argparse
import logging
import sys
import textwrap

import src.definitions as defs
import src.exceptions as ac_exc

parser = argparse.ArgumentParser(
    epilog=textwrap.dedent("""
    NOTE: Adjusting video dimensions changes overall VRAM allocation, which may
          lead to programs running out of general-purpose RAM during execution,
          as VRAM is dynamically allocated from general purpose RAM during
          machine initialization
    """),
    formatter_class=argparse.RawTextHelpFormatter)
logger = logging.getLogger("ac100")

# AC100 emulator
class AC100:

    REGS: bytearray
    RAM: bytearray
    PC: int
    PS: int                     # status register
    SP: int                     # stack pointer

    def __init__(self):
        self.REGS = [[0x00 for i in range(defs.BYTES_PER_WORD)]\
                     for j in range(defs.NUM_REGISTERS)]
        self.RAM = bytearray(defs.ADDRESS_SIZE)
        self.PS = 0x00          # 0b00000000
        self.SP = defs.STACK_MIN
        self.PC = self.SP + 1
        self.VIDEO_WIDTH: int = defs.DEFAULT_VIDEO_COLUMNS
        self.VIDEO_HEIGHT: int = defs.DEFAULT_VIDEO_ROWS
        self.VRAM_START: int = defs.DEFAULT_VRAM_START


    def initialize_VRAM(self, args) -> None:
        """
        Set up VRAM given a set of command-line arguments

        Parameters:
        args: the args from the argument parser

        If either of the dimensions found on the command line are invalid in any
        way, report it and use the default dimensions
        """
        dimensions = [defs.DEFAULT_VIDEO_ROWS, defs.DEFAULT_VIDEO_COLUMNS]
        try:
            dimensions = check_video_dimensions(args)
        except ac_exc.NegativeVideoDimensionError as e:
            logger.error(e)
            dimensions = [defs.DEFAULT_VIDEO_ROWS, defs.DEFAULT_VIDEO_COLUMNS]
        except ac_exc.VRAMTooLargeError as e:
            logger.error(e)
            dimensions = [defs.DEFAULT_VIDEO_ROWS, defs.DEFAULT_VIDEO_COLUMNS]

        self.VIDEO_HEIGHT = dimensions[0]
        self.VIDEO_WIDTH = dimensions[1]


def check_video_dimensions(args) -> [int]:
    """
    Ensure video dimensions are valid

    Make sure video dimensions
    a: Aren't negative: having negative dimensions makes no sense!
    b: Don't cause VRAM to encroach on stack portion of memory

    We don't have to check explicitly check if VRAM > total RAM, because if the
    VRAM encroaches on the stack, then there's no general-purpose RAM
    left anyways

    Parameters:
    args: the args from the argument parser; check if the user requested
    custom dimensions and, if so, make sure they're valid

    Return:
    The final dimensions to use for VRAM allocation.  The first value is the
    video height; the second value is the video width

    If either user-supplied dimension is negative, raise a
    NegativeVideoDimensionError

    If either user-supplied dimension would cause the VRAM to encroach on the
    stack, raise a VRAMTooLargeError
    """
    dimensions: [int] = [defs.DEFAULT_VIDEO_ROWS, defs.DEFAULT_VIDEO_COLUMNS]
    rows: int = int(args.rows)
    columns: int = int(args.columns)
    new_size: int = defs.DEFAULT_VIDEO_ROWS * defs.DEFAULT_VIDEO_COLUMNS
    if columns != defs.DEFAULT_VIDEO_COLUMNS:
        if columns < 0:
            raise ac_exc.NegativeVideoDimensionError("column")

        new_size = defs.DEFAULT_VIDEO_ROWS * columns
        if defs.ADDRESS_SIZE - new_size < defs.STACK_MIN:
            raise ac_exc.VRAMTooLargeError("column", columns)
        dimensions[1] = columns

    if rows != defs.DEFAULT_VIDEO_ROWS:
        if rows < 0:
            raise ac_exc.NegativeVideoDimensionError("row")

        new_size = defs.DEFAULT_VIDEO_COLUMNS * rows
        if defs.ADDRESS_SIZE - new_size < defs.STACK_MIN:
            raise ac_exc.VRAMTooLargeError("row", rows)
        dimensions[0] = rows

    return dimensions


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


def setup_logger(logger, args):
    format = "[%(levelname)s]: %(funcName)s:%(lineno)d: %(message)s"
    logging.basicConfig(format=format, level=args.loglevel.upper())


def main():
    setup_parser(parser)
    machine = AC100()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    dimensions = check_video_dimensions(args)
    machine.initialize_VRAM(args)


if __name__ == "__main__":
    main()
