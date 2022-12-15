import argparse
import logging
import sys
import typing

import src.definitions as defs
import src.exceptions as ac_exc

logger = logging.getLogger("ac100asm")
parser = argparse.ArgumentParser()

class LabelDict(typing.TypedDict):
    name: str                   # the label
    offset: int                 # address the label refers to

# Assembler for the AC100
class AC100ASM:
    labels: LabelDict


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


    def parse_int(self, token) -> int:
        """
        Parse an integer.

        The token may represent an integer in binary, decimal, or hexadecimal,
        but must be in the range -32767--+32768 or 0--65535, depending on the
        sign

        Parameters:
        token: the token to be parsed

        Return: if token is a valid representation of an integer and in range,
        sign-dependent, return the number.  Otherwise, raise ValueError
        """
        SIGNED_MIN = -32768
        SIGNED_MAX = 32767
        UNSIGNED_MIN = 0
        UNSIGNED_MAX = 65535
        number: int = None
        if token.startswith(defs.BINARY_PREFIX):
            pass                # parse binary
        elif token.startswith(defs.HEX_PREFIX):
            pass                # parse hex
        else:
            try:
                number = int(token)
                if token.startswith("-") and number < SIGNED_MIN:
                    raise ValueError(f"Value {number} too negative for 16 bits")
                else:
                    if number > UNSIGNED_MAX:
                        raise ValueError(f"Number {number} too large for 16 bits")
            except ValueError:  # float or out of 16-bit range
                logger.error("Could not parse 16-bit integer from from '%s'",
                             token)
                number = None

        return number


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


def setup_parser(parser) -> None:
    """ Set up ArgumentParser """
    parser.add_argument("infile", help="The source file to assemble")
    parser.add_argument("-l", "--loglevel", default="error",
                        choices=["debug", "info", "warning", "error"],
                        metavar="level", help="logging level")
    parser.add_argument("-o", "--outfile", default="out.bin", metavar="file",
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


if __name__ == "__main__":
    main()
