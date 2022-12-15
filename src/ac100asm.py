import argparse
import logging
import sys
import typing

import src.definitions as defs
import src.exceptions as ac_exc

logger = logging.getLogger("ac100asm")
parser = argparse.ArgumentParser()

DEFAULT_OUTPUT: str = "out.bin"

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
        SIGNED_MAX = 32767
        UNSIGNED_MIN = 0
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



    def assemble(self, infile: typing.TextIO) -> bool:
        """
        Assemble a binary from source code.

        Parameters:
        infile: the file object associated with the source code file

        Return:
        On success, return True.  On failure, return False
        """
        self.lineno = 0
        for source_line in infile:
            self.lineno += 1
            tokens = self.tokenize_line(source_line)
            if tokens is None:  # empty line, go on to the next one
                continue
            match tokens[0]:    # opcode
                case ";":       # comment; do nothing
                    continue

        return True


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
    with open(args.infile) as f:
        assembler.assemble(f)


if __name__ == "__main__":
    main()
