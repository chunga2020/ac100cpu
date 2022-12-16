import argparse
import logging
import sys
import typing

import src.definitions as defs
import src.exceptions as ac_exc

logger = logging.getLogger("ac100asm")
parser = argparse.ArgumentParser()

DEFAULT_OUTPUT: str = "out.bin"

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

class LabelDict(typing.TypedDict):
    name: str                   # the label
    offset: int                 # address the label refers to

# Assembler for the AC100
class AC100ASM:
    labels: LabelDict

    def __init__(self):
        self.labels = LabelDict()
        self.lineno: int = 0    # line number of current source line
        self.default_output: str = DEFAULT_OUTPUT


    def parse_register_name(self, token: str) -> int:
        """
        Parse a register name from a token

        Parameters:
        token: the token to parse

        Return: the number corresponding to the specified register

        Because arrays start at 0 but the register names start at 1, a valid
        register name will be decremented before it is returned
        """
        if not token.startswith(defs.REGISTER_PREFIX):
            raise ac_exc.RegisterNameMissingPrefixError(token)

        number: int = int(token[1:]) # remove prefix
        if number < defs.REGISTER_MIN or number > defs.REGISTER_MAX:
            raise ac_exc.InvalidRegisterNameError(token, defs.REGISTER_MIN,
                                                  defs.REGISTER_MAX)

        number -= 1
        return number


    def parse_int(self, token) -> bytes:
        """
        Parse an integer.

        The token may represent an integer in binary, decimal, or hexadecimal,
        but must be in the range -32767--+32768 or 0--65535, depending on the
        sign

        Parameters:
        token: the token to be parsed

        Return: if token is a valid representation of an integer and in range,
        sign-dependent, return hex bytes corresponding to the number.
        Otherwise, return None
        """
        SIGNED_MIN = -32768
        UNSIGNED_MAX = 65535
        number: int = None
        if token.startswith(defs.BINARY_PREFIX):
            token = token[2:]   # strip prefix
            if len(token) > defs.WORD_SIZE:
                raise ValueError(f"Value '{token}' too large for 16 bits")
            number = int(token, 2)
            if number > UNSIGNED_MAX:
                raise ValueError(f"Binary value {token} too big for 16 bits")
            number = bytes([number >> 8 & 0xff, number & 0xff])
        elif token.startswith(defs.HEX_PREFIX):
            token = token[2:]   # strip prefix
            if len(token) % 2 == 1:
                if len(token) == 1:
                    token = "0" + token
                else:
                    raise ValueError(f"Invalid hex value '{token}'")
            number = bytes.fromhex(token)

            if len(number) > defs.BYTES_PER_WORD:
                number = None
                raise ValueError(f"Hex value {token} does not fit in 16 bits")
        else:
            try:
                number = int(token)
                if token.startswith("-") and number < SIGNED_MIN:
                    raise ValueError(f"Value {number} too negative for 16 bits")
                else:
                    if number > UNSIGNED_MAX:
                        raise ValueError(f"Number {number} too large for 16 bits")
            except ValueError:  # float or out of 16-bit range
                logger.error("Could not parse 16-bit integer from '%s'",
                             token)
                number = None
            if number is not None:
                number = bytes([number >> 8 & 0xff, number & 0xff])

        return number


    def parse_address(self, token) -> bytes:
        """
        Parse a hexadecimal address

        Parameters:
        token: the token to parse

        Return:
        bytes corresponding to the address
        """
        if not token.startswith(defs.HEX_PREFIX):
            raise ValueError("Addresses must be given in hexadecimal")

        # we keep the hex prefix, because parse_int takes care of it
        # len of prefix is 2, expected len of address is 4 -> 2 + 4 = 6
        if len(token) != 6:
            raise ValueError("Addresses should be 16 bits wide (4 hex digits)")
        address = self.parse_int(token)

        return address


    def tokenize_line(self, line) -> [str]:
        """
        Split a source line into tokens

        Parameters:
        line: the line to tokenize

        Return: a list of the tokens in the line
        """
        line = line.strip()
        if line == "":          # ignore whitespace-only lines
            tokens = None
        else:
            tokens = line.split(' ')
        return tokens


    def _assemble_ldi(self, tokens) -> bytes:
        """
        Assemble an LDI instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        Return the bytecode on success, or None on error
        """
        bytecode: bytes = b"\x00"
        dest_reg: int = -1
        try:
            dest_reg = self.parse_register_name(tokens[1])
        except (ac_exc.RegisterNameMissingPrefixError,
                ac_exc.InvalidRegisterNameError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += dest_reg.to_bytes(1, byteorder='big')
        try:
            word: bytes = self.parse_int(tokens[2])
        except ValueError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += word
        if len(bytecode) != 4:
            logger.error(f"Bytecode should be 4 bytes, is {len(bytecode)}")
            return None

        return bytecode


    def _assemble_ldr(self, tokens: [str]) -> bytes:
        """
        Assemble an LDR instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b"\x01"
        dest_reg: int = -1
        try:
            dest_reg = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += dest_reg.to_bytes(1, byteorder='big')
        src_reg: int = -1
        try:
            src_reg = self.parse_register_name(tokens[2])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += src_reg.to_bytes(1, byteorder='big')
        bytecode += b"\x00"
        if len(bytecode) != 4:
            logger.error(f"Bytecode should be 4 bytes, but is {len(bytecode)}")
            return None
        return bytecode


    def _assemble_st(self, tokens: [str]) -> bytes:
        """
        Assemble an ST instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b"\x10"
        src_reg: int = -1
        try:
            src_reg = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError):
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += src_reg.to_bytes(1, byteorder='big')
        address: bytes = b""
        try:
            address = self.parse_address(tokens[2])
        except ValueError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
        bytecode += address
        if len(bytecode) != 4:
            logger.error(f"Bytecode should be 4 bytes, but is {len(bytecode)}")
            return None
        return bytecode


    def _assemble_halt(self):
        bytecode: bytes = b"\xfe\xff\xfe\xff"
        return bytecode


    def assemble(self, infile: typing.TextIO) -> bytes:
        """
        Assemble a binary from source code.

        Parameters:
        infile: the file object associated with the source code file

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        self.lineno = 0
        bytecode: bytes = b""
        next_line: bytes = None # next assembled bytecode
        for source_line in infile:
            self.lineno += 1
            tokens = self.tokenize_line(source_line)
            if tokens is None:  # empty line, go on to the next one
                continue
            match tokens[0]:    # opcode
                case "LDI":
                    next_line = self._assemble_ldi(tokens)
                    if next_line is None:
                        logger.error(f"Failed to assemble {tokens[0]}")
                        return None
                    bytecode += next_line
                case "LDR":
                    next_line = self._assemble_ldr(tokens)
                    if next_line is None:
                        logger.error(f"Failed to assemble {tokens[0]}")
                        return None
                    bytecode += next_line
                case "ST":
                    next_line = self._assemble_st(tokens)
                    if next_line is None:
                        logger.error(f"Failed to assemble {tokens[0]}")
                        return None
                    bytecode += next_line
                case "HALT":
                    next_line = self._assemble_halt()
                    bytecode += next_line
                case ";":       # comment; do nothing
                    continue

        return bytecode


def setup_parser(parser) -> None:
    """ Set up ArgumentParser """
    parser.add_argument("infile", help="The source file to assemble")
    parser.add_argument("-l", "--loglevel", default="error",
                        choices=["debug", "info", "warning", "error"],
                        metavar="level", help="logging level")
    parser.add_argument("-o", "--outfile", default=DEFAULT_OUTPUT,
                        metavar="file",
                        help="name to use for output file (default: %(default)s)")


def setup_logger(level) -> None:
    """
    Set up logger

    Parameters:
    level: the level to use
    """
    format = "[%(levelname)s]:%(funcName)s:%(lineno)d: %(message)s"
    logging.basicConfig(format=format, level=logging.getLevelName(level))


def main():
    assembler = AC100ASM()
    setup_parser(parser)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    setup_logger(args.loglevel.upper())
    with open(args.infile) as f, open(args.outfile, "wb") as f2:
        bytecode: bytes = assembler.assemble(f)
        if bytecode is not None:
            f2.write(bytecode)


if __name__ == "__main__":
    main()
