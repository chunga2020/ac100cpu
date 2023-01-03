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

# Mapping from opcodes to mnemonics
 # opcodes all one byte
INSTRUCTION_TABLE = ["NONE" for i in range(2 ** defs.BYTE)]
INSTRUCTION_TABLE[0x00] = "LDI"
INSTRUCTION_TABLE[0x01] = "LDR"
INSTRUCTION_TABLE[0x02] = "LDM"
INSTRUCTION_TABLE[0x10] = "ST"
INSTRUCTION_TABLE[0x11] = "STH"
INSTRUCTION_TABLE[0x12] = "STL"
INSTRUCTION_TABLE[0x20] = "CMP"
INSTRUCTION_TABLE[0x21] = "CMI"
INSTRUCTION_TABLE[0x30] = "JE"
INSTRUCTION_TABLE[0x31] = "JG"
INSTRUCTION_TABLE[0x32] = "JGE"
INSTRUCTION_TABLE[0x33] = "JL"
INSTRUCTION_TABLE[0x34] = "JLE"
INSTRUCTION_TABLE[0x35] = "JMP"
INSTRUCTION_TABLE[0x40] = "ADDI"
INSTRUCTION_TABLE[0x41] = "ADDR"
INSTRUCTION_TABLE[0x42] = "INC"
INSTRUCTION_TABLE[0x43] = "SUBI"
INSTRUCTION_TABLE[0x44] = "SUBR"
INSTRUCTION_TABLE[0x45] = "DEC"
INSTRUCTION_TABLE[0xE0] = "PUSH"
INSTRUCTION_TABLE[0xE1] = "POP"
INSTRUCTION_TABLE[0xFE] = "HALT"
INSTRUCTION_TABLE[0xFF] = "NOP"

# AC100 emulator
class AC100:

    REGS: bytearray
    RAM: bytearray
    PC: int
    PS: int                     # status register
    SP: int                     # stack pointer

    # flags
    FLAG_CARRY = 0x1
    FLAG_ZERO = 0x2
    FLAG_OVERFLOW = 0x4
    FLAG_NEGATIVE = 0x8

    VALID_FLAGS = [FLAG_NEGATIVE, FLAG_OVERFLOW, FLAG_ZERO, FLAG_CARRY]
    FLAG_NAMES = {
        FLAG_CARRY: "C",
        FLAG_ZERO: "Z",
        FLAG_OVERFLOW: "V",
        FLAG_NEGATIVE: "N"
    }

    # for clearing flags
    SHIFT_AMOUNTS = {
        FLAG_NEGATIVE: 3,
        FLAG_OVERFLOW: 2,
        FLAG_ZERO: 1,
        FLAG_CARRY: 0
    }

    def flag_set(self, flag: int) -> bool:
        """
        Set a processor status flag.

        Parameters:
        flag: the flag to set

        Return:
        If the flag is valid, return True.  Else, return False.
        """
        if flag not in self.VALID_FLAGS:
            logger.error(f"Invalid flag {flag}")
            return False
        self.PS |= flag
        return True


    def flag_clear(self, flag: int) -> bool:
        """
        Clear a processor status flag.

        Parameters:
        flag: the flag to clear

        Return:
        If the flag is valid, return True.  Else, return False.
        """
        if flag not in self.VALID_FLAGS:
            logger.error(f"Invalid flag {flag}")
            return False
        self.PS &= ~(0x01 << self.SHIFT_AMOUNTS[flag])
        return True


    def flag_read(self, flag: int) -> bool:
        """
        Check if a flag is set.

        Parameters:
        flag: the flag to read

        Return:
        If the flag is set, return True.  Else, return False.  If the flag is
        invalid, return None.
        """
        if flag not in self.VALID_FLAGS:
            logger.error(f"Invalid flag {flag}")
            return None
        return self.PS & flag == flag


    def flag_set_or_clear(self, flag: int, condition: bool) -> bool:
        if flag not in self.VALID_FLAGS:
            logger.error(f"Invalid flag {flag}")
            return None
        if condition:
            return self.flag_set(flag)
        else:
            return self.flag_clear(flag)


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


    def load_ram(self, bytecode: bytes) -> None:
        """
        Load a program into memory.

        Parameters:
        bytecode: the bytecode to load
        """
        program_len: int = len(bytecode)

        for i in range(program_len):
            self.RAM[self.PC + i] = bytecode[i]


    def fetch_instruction(self) -> bytes:
        return [self.RAM[self.PC + i] for i in range(4)]


    def _increment_pc(self):
        self.PC += 4


    def dump_registers(self) -> None:
        """ Dump register contents to standard output. """
        for i in range(defs.NUM_REGISTERS):
            if (i + 1) % 4 == 0:
                print(f"R{i + 1}: 0x{self.REGS[i][0] << 8 | self.REGS[i][1]:04x}")
            else:
                print(f"R{i + 1}: 0x{self.REGS[i][0] << 8 | self.REGS[i][1]:04x}",
                      end='\t')


    def _exec_ldi(self, instruction: bytes) -> None:
        """
        Execute an LDI instruction.

        Parameters:
        instruction: the instruction to execute
        """
        register = instruction[1]
        self.REGS[register][0] = instruction[2]
        self.REGS[register][1] = instruction[3]
        value = instruction[2] << 8 | instruction[3]

        self.flag_set_or_clear(self.FLAG_ZERO, value == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, value & 0x8000 == 0x8000)


    def _exec_ldr(self, instruction: bytes) -> None:
        dest_reg = instruction[1]
        src_reg = instruction[2]

        self.REGS[dest_reg][0] = self.REGS[src_reg][0]
        self.REGS[dest_reg][1] = self.REGS[src_reg][1]
        value = self.REGS[dest_reg][0] << 8 | self.REGS[dest_reg][1]

        self.flag_set_or_clear(self.FLAG_ZERO, value == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, value & 0x8000 == 0x8000)


    def _exec_ldm(self, instruction: bytes) -> None:
        dest_reg = instruction[1]
        address = instruction[2] << 8 | instruction[3]
        if address < defs.STACK_MIN:
            logger.warning("Loading value from stack memory")
        self.REGS[dest_reg][0] = self.RAM[address]
        self.REGS[dest_reg][1] = self.RAM[address + 1]

        value = self.REGS[dest_reg][0] << 8 | self.REGS[dest_reg][1]

        self.flag_set_or_clear(self.FLAG_ZERO, value == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, value & 0x8000 == 0x8000)


    def _exec_st(self, instruction: bytes) -> None:
        register = instruction[1]
        dest_address = instruction[2] << 8 | instruction[3]
        if dest_address < defs.STACK_MIN:
            # trying to store in stack: forbidden
            msg = "Programs may not store data in the stack "
            msg += f"([0x{defs.STACK_MAX:04x}--0x{defs.STACK_MIN:04x}])"
            logger.error(msg)
            sys.exit(1)
        self.RAM[dest_address] = self.REGS[register][0]
        self.RAM[dest_address+1] = self.REGS[register][1]


    def decode_execute_instruction(self, instruction) -> bool:
        """
        Decode and execute the next instruction

        Parameters:
        instruction: the instruction to decode and execute

        Return:
        On success, return True.  On failure, return False.

        HALT never returns to the caller, instead causing the Python interpreter
        to exit.
        """
        if len(instruction) != 4:
            logger.error("Expected 4-byte instruction")
            return False

        opcode: bytes = INSTRUCTION_TABLE[instruction[0]]
        match opcode:
            case "LDI":
                self._exec_ldi(instruction)
                self._increment_pc()
            case "LDR":
                self._exec_ldr(instruction)
                self._increment_pc()
            case "LDM":
                self._exec_ldm(instruction)
                self._increment_pc()
            case "ST":
                self._exec_st(instruction)
                self._increment_pc()
            case "HALT": sys.exit(0)
            case "NOP":
                self._increment_pc()
            case _:
                logger.error(f"Unknown or unimplemented opcode {opcode}")
                return False

        return True


    def run(self):
        while self.PC < self.VRAM_START:
            instruction = self.fetch_instruction()
            ok = self.decode_execute_instruction(instruction)
            if not ok:
                logger.error(f"{INSTRUCTION_TABLE[instruction[0]]} failed")
                return -1


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

    with open(args.binary, "r") as f:
        machine.load_ram(f.read())

    machine.run()

    return 0


if __name__ == "__main__":
    main()
