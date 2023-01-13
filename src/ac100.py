import atexit
import argparse
import curses
import logging
import signal
import sys

import src.definitions as defs
import src.exceptions as ac_exc

def end_curses_exit():
    if not curses.isendwin():
        curses.endwin()
    sys.exit(0)


atexit.register(end_curses_exit)  # always clean up curses on normal exit

def ctrl_c_handler(signum, frame):
    """ End curses mode on CTRL-C """
    end_curses_exit()

signal.signal(signal.SIGINT, ctrl_c_handler)


parser = argparse.ArgumentParser()
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
INSTRUCTION_TABLE[0x20] = "CMR"
INSTRUCTION_TABLE[0x21] = "CMI"
INSTRUCTION_TABLE[0x30] = "JZ"
INSTRUCTION_TABLE[0x31] = "JNZ"
INSTRUCTION_TABLE[0x32] = "JC"
INSTRUCTION_TABLE[0x33] = "JNC"
INSTRUCTION_TABLE[0x34] = "JN"
INSTRUCTION_TABLE[0x35] = "JP"
INSTRUCTION_TABLE[0x36] = "JV"
INSTRUCTION_TABLE[0x37] = "JNV"
INSTRUCTION_TABLE[0x38] = "JMP"
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
        self.PC = defs.CODE_START
        self.VIDEO_WIDTH: int = defs.VIDEO_COLUMNS
        self.VIDEO_HEIGHT: int = defs.VIDEO_ROWS
        self.VRAM_START: int = defs.VRAM_START
        self.stdscr = None
        self.display = None


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


    def initialize_video(self) -> None:
        """ Set up the curses-based emulated video display. """
        stdscr = curses.initscr()
        self.stdscr = stdscr
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        term_height = curses.LINES
        term_width = curses.COLS

        window_width = self.VIDEO_WIDTH + 2 # padding on both sides
        window_height = self.VIDEO_HEIGHT + 2 # padding on top and bottom

        begin_x = term_width / 2 - window_width / 2
        begin_y = term_height / 2 - window_height / 2
        display = curses.newwin(window_height, window_width, begin_y, begin_x)
        self.display = display


    def end_video(self) -> None:
        """ Clean up curses display. """
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()


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


    def _exec_load(self, instruction: bytes) -> None:
        """ Execute a load instruction (LDI|LDR|LDM). """
        opcode = instruction[0]
        mnemonic = INSTRUCTION_TABLE[opcode]
        dest_reg = instruction[1]

        match mnemonic:
            case "LDI":
                self.REGS[dest_reg][0] = instruction[2]
                self.REGS[dest_reg][1] = instruction[3]
            case "LDR":
                src_reg = instruction[2]
                self.REGS[dest_reg][0] = self.REGS[src_reg][0]
                self.REGS[dest_reg][1] = self.REGS[src_reg][1]
            case "LDM":
                address = instruction[2] << 8 | instruction[3]
                self.REGS[dest_reg][0] = self.RAM[address]
                self.REGS[dest_reg][1] = self.RAM[address + 1]

        value = self.REGS[dest_reg][0] << 8 | self.REGS[dest_reg][1]

        self.flag_set_or_clear(self.FLAG_ZERO, value == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, value & 0x8000 == 0x8000)


    def _st_stack_error(self):
        msg = "Programs may not store data in the stack "
        msg += f"([0x{defs.STACK_MAX:04x}--0x{defs.STACK_MIN:04x}])"
        logger.error(msg)


    def _exec_store(self, instruction: bytes) -> None:
        opcode = instruction[0]
        mnemonic = INSTRUCTION_TABLE[opcode]
        register = instruction[1]
        dest_address = instruction[2] << 8 | instruction[3]
        if dest_address < defs.STACK_MIN:
            # trying to store in stack: forbidden
            self._st_stack_error()
            sys.exit(1)
        match mnemonic:
            case "ST":
                self.RAM[dest_address] = self.REGS[register][0]
                self.RAM[dest_address+1] = self.REGS[register][1]
            case "STH":
                self.RAM[dest_address] = self.REGS[register][0]
            case "STL":
                self.RAM[dest_address] = self.REGS[register][1]


    def _add_bits(self, a: int, b: int, carry_in: int) -> (int, int):
        """
        Add two one-bit numbers.

        This implements a full adder, making more straightfoward the logic of
        determining if an operation should set or clear the carry flag.

        Parameters:
        - a: the first number to be added
        - b: the second number to be added
        - carry_in: the carry in

        Return:
        A 2-tuple (carry_out, sum), corresponding to the resulting carryout and
        sum bits of the addition a + b. If any of the arguments are invalid,
        return None.
        """
        valid_bits = [0x0, 0x1]
        if a not in valid_bits:
            logger.error(f"Invalid bit a={a:#x}")
            return None
        if b not in valid_bits:
            logger.error(f"Invalid bit b={b:#x}")
            return None
        if carry_in not in valid_bits:
            logger.error(f"Invalid bit carry_in={carry_in:#x}")
            return None
        sum = a ^ b ^ carry_in
        carry_out = (a & b) | ((a^b) & carry_in)

        return (carry_out, sum)


    def _ripple_add(self, a: int, b: int) -> (bool, int, bool):
        """
        Ripple-carry add two numbers.

        Parameters:
        - a: the first number to add
        - b: the second number to add

        Return:
        A 3-tuple (carry_set, sum, overflow_set) corresponding to:
        - True/False, depending on whether there was carry out of the
        most-significant bit
        - the low 16 bits of a + b
        - True/False, depending on whether there was overflow into the sign bit
        """
        # final answer, unsigned
        final = 0x0
        # initially no carry-in
        carry_in = 0x0
        sign_a = (a >> 15) & 0x1
        sign_b = (b >> 15) & 0x1

        for i in range(defs.WORD_SIZE):
            a_i = (a >> i) & 0x1
            b_i = (b >> i) & 0x1
            result = self._add_bits(a_i, b_i, carry_in)
            carry_in = result[0] # use carryout as carryin of the next bit
            final += (result[1] << i)
        final &= 0xffff
        sign_final = (final >> 15) & 0x1
        overflow_set = True if ((~(sign_a | sign_b) & sign_final) \
                                | ((sign_a & sign_b) & ~sign_final)) else False
        carry_set: bool = (carry_in == 1)

        return (carry_set, final, overflow_set)


    def _exec_cmp(self, instruction: bytes) -> None:
        opcode = instruction[0]
        mnemonic = INSTRUCTION_TABLE[opcode]

        b = 0
        a_reg = instruction[1]
        a = self.REGS[a_reg][0] << 8 | self.REGS[a_reg][1]
        match mnemonic:
            case "CMR":
                b_reg = instruction[2]
                b = self.REGS[b_reg][0] << 8 | self.REGS[b_reg][1]
            case "CMI":
                b = instruction[2] << 8 | instruction[3]

        c_set, sum, _ = self._ripple_add(a, (~b + 1) & 0xffff)
        self.flag_set_or_clear(self.FLAG_CARRY, c_set)
        self.flag_set_or_clear(self.FLAG_ZERO, sum == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE,
                               (sum >> 15) & 0x1 == 1)


    def _branch_on_flag_set(self, flag, address) -> None:
        """
        Conditionally branch execution if a flag is set.

        Parameters:
        - flag: the flag to check
        - address: the address to jump to if the flag is set
        """
        if self.flag_read(flag):
            self.PC = address
        else:
            self._increment_pc() # continue normal execution


    def _branch_on_flag_clear(self, flag, address) -> None:
        """
        Conditionally branch execution if a flag is cleared.

        Parameters:
        - flag: the flag to check
        - address: the address to jump to if the flag is cleared
        """
        if not self.flag_read(flag):
            self.PC = address
        else:
            self._increment_pc()


    def _exec_jump(self, instruction: bytes) -> None:
        opcode = instruction[0]
        mnemonic = INSTRUCTION_TABLE[opcode]
        address = instruction[2] << 8 | instruction[3]
        # high-address end of the stack is the same address as the start of the
        # code section, so we don't want to raise an exception if address is the
        # high end of the stack
        if address < defs.STACK_MIN:
            raise ac_exc.StackJumpError(address)
        # VRAM is not executable code
        if address >= self.VRAM_START:
            raise ac_exc.VRAMJumpError(address, self.VRAM_START,
                                       defs.ADDRESS_MAX)
        if address % 4 != 0:
            raise ac_exc.PcAlignmentError(address)

        match mnemonic:
            case "JZ": self._branch_on_flag_set(self.FLAG_ZERO, address)
            case "JNZ": self._branch_on_flag_clear(self.FLAG_ZERO, address)

            case "JC": self._branch_on_flag_set(self.FLAG_CARRY, address)
            case "JNC": self._branch_on_flag_clear(self.FLAG_CARRY, address)

            case "JN": self._branch_on_flag_set(self.FLAG_NEGATIVE, address)
            case "JP": self._branch_on_flag_clear(self.FLAG_NEGATIVE, address)

            case "JV": self._branch_on_flag_set(self.FLAG_OVERFLOW, address)
            case "JNV": self._branch_on_flag_clear(self.FLAG_OVERFLOW, address)

            case "JMP": self.PC = address # unconditional jump


    def _exec_add_sub(self, instruction: bytes) -> None:
        """
        Execute an ADD* or SUB* instruction.

        Parameters:
        - instruction: the bytecode to execute

        These operations can be merged into one handler because we use 2's
        complement arithmetic.
        """
        opcode = instruction[0]
        mnemonic = INSTRUCTION_TABLE[opcode]
        register = instruction[1]
        a = self.REGS[register][0] << 8 | self.REGS[register][1]
        b = 0
        match mnemonic:
            case "ADDI" | "SUBI":
                b = instruction[2] << 8 | instruction[3]
            case "ADDR" | "SUBR":
                b_reg = instruction[2]
                b = self.REGS[b_reg][0] << 8 | self.REGS[b_reg][1]
        neg_b = ~b + 1          # for subtraction only

        carry_set = 0
        sum = 0
        overflow_set = 0

        match mnemonic:
            case "ADDI" | "ADDR":
                carry_set, sum, overflow_set = self._ripple_add(a, b)
            case "SUBI" | "SUBR":
                carry_set, sum, overflow_set = self._ripple_add(a, neg_b)

        self.REGS[register][0] = sum >> 8 & 0xff
        self.REGS[register][1] = sum & 0xff

        self.flag_set_or_clear(self.FLAG_CARRY, carry_set)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, sum >> 15 & 0x1 == 1)
        self.flag_set_or_clear(self.FLAG_OVERFLOW, overflow_set)
        self.flag_set_or_clear(self.FLAG_ZERO, sum == 0)


    def _exec_inc(self, instruction: bytes) -> None:
        register = instruction[1]
        value = (self.REGS[register][0] << 8 | self.REGS[register][1]) & 0xffff
        value += 1
        value &= 0xffff

        self.REGS[register][0] = (value >> 8) & 0xff
        self.REGS[register][1] = value & 0xff

        self.flag_set_or_clear(self.FLAG_ZERO, value & 0xffff == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, value >> 15 & 0x1 == 1)


    def _exec_dec(self, instruction: bytes) -> None:
        register = instruction[1]
        value = (self.REGS[register][0] << 8 | self.REGS[register][1]) & 0xffff
        value -= 1
        value &= 0xffff

        self.REGS[register][0] = (value >> 8) & 0xff
        self.REGS[register][1] = value & 0xff

        self.flag_set_or_clear(self.FLAG_ZERO, value & 0xffff == 0)
        self.flag_set_or_clear(self.FLAG_NEGATIVE, value >> 15 & 0x1 == 1)


    def _decrement_sp(self):
        self.SP -= 2


    def _exec_push(self, instruction: bytes) -> None:
        register = instruction[1]
        # stack grows down from high addresses to low addresses
        if self.SP == defs.ADDRESS_MIN:
            raise ac_exc.StackOverflowError
        # make sure stack pointer remains 2-byte aligned
        if self.SP % 2 != 0:
            raise ac_exc.StackPointerAlignmentError(self.SP)
        self._decrement_sp()
        self.RAM[self.SP] = self.REGS[register][0]
        self.RAM[self.SP + 1] = self.REGS[register][1]


    def _increment_sp(self):
        self.SP += 2


    def _exec_pop(self, instruction: bytes) -> None:
        register = instruction[1]
        if self.SP == defs.STACK_MIN:
            raise ac_exc.StackEmptyError
        if self.SP % 2 != 0:
            raise ac_exc.StackPointerAlignmentError(self.SP)
        self.REGS[register][0] = self.RAM[self.SP]
        self.REGS[register][1] = self.RAM[self.SP + 1]
        self._increment_sp()


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
            case "LDI" | "LDR" | "LDM":
                self._exec_load(instruction)
                self._increment_pc()
            case "ST" | "STH" | "STL":
                self._exec_store(instruction)
                self._increment_pc()
            case "CMR" | "CMI":
                self._exec_cmp(instruction)
                self._increment_pc()
            case "JZ" | "JNZ" | "JC" | "JNC" | "JN" | "JP" | "JV" | "JNV" | \
                    "JMP":
                # no need to do PC increment; that depends on whether a jump
                # occurs or not, so _exec_jump handles it (more precisely, its
                # helper functions handle PC manipulation)
                self._exec_jump(instruction)
            case "INC":
                self._exec_inc(instruction)
                self._increment_pc()
            case "DEC":
                self._exec_dec(instruction)
                self._increment_pc()
            case "PUSH":
                try:
                    self._exec_push(instruction)
                    self._increment_pc()
                except (ac_exc.StackOverflowError,
                        ac_exc.StackPointerAlignmentError) as e:
                    logger.error(e)
                    return False
            case "POP":
                try:
                    self._exec_pop(instruction)
                    self._increment_pc()
                except (ac_exc.StackEmptyError,
                        ac_exc.StackPointerAlignmentError) as e:
                    logger.error(e)
                    return False
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
                self.end_video()
                logger.error(f"{INSTRUCTION_TABLE[instruction[0]]} failed")
                return -1

        self.end_video()
        return 0


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
    parser.add_argument("-d", "--debug-info", default="none",
                        help="Machine state to print for debugging purposes "
                        "(default: %(default)s)",
                        choices=["none", "registers", "ram", "flags", "all"])
    parser.add_argument("-l", "--loglevel", default="error",
                        help="Logging level (default: %(default)s)",
                        metavar="level",
                        choices=["debug", "info", "warning", "error", "critical"])


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
    machine.initialize_VRAM(args)

    with open(args.binary, "rb") as f:
        machine.load_ram(f.read())

    machine.initialize_video()
    return machine.run()


if __name__ == "__main__":
    main()
