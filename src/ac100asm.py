import argparse
import logging
import re
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
        self.offset = defs.CODE_START # code section starts here


    def parse_label(self, tokens: [str]) -> str:
        """
        Parse a label.

        Parameters:
        tokens: the line to be parsed

        Return:
        On success, return the label found.  On failure, return None.
        """
        if len(tokens) != 1:
            logger.error(f"Too many tokens for label line: '{tokens}'")
            return None
        # Number-only labels not allowed
        # Underscore-only labels not allowed
        # (leading underscores followed by alphanumerics okay)
        pattern = re.compile(r"^([a-zA-Z]\w*)")
        m = pattern.match(tokens[0])
        if m is None:
            logger.error(f"Invalid label {tokens[0]}")
            return m
        label = m.group(1)
        logger.debug(f"Found label {label} at offset 0x{self.offset:04x}")

        return label


    def add_label(self, label: str) -> None:
        self.labels[label] = self.offset


    def get_label_offset(self, label: str) -> int:
        """
        Get a label's corresponding offset.

        Parameters:
        label: the label to look up

        Return:
        If the label exists, return its corresponding offset.  Else, return
        None.
        """
        return self.labels.get(label, None)


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


    def parse_register_indirect(self, token: str) -> int:
        """
        Parse a register-indirect address.

        Parameters:
        token: the token to parse

        Return: the number corresponding to the specified register
        """
        pattern = re.compile(r"\[(R\d{1,2})\]")
        match = pattern.match(token)
        if match is not None:
            register_tok = match.group(1)
            return self.parse_register_name(register_tok)


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
            if len(number) == 1:
                number = b"\x00" + number

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
                msg: str = f"Could not parse 16-bit integer from '{token}'"
                raise ValueError(msg)
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


    def _check_len(self, bytecode: bytes) -> bytes:
        """
        Check that an assembled bytecode instruction is the correct size.

        For the AC100, all instructions should be four bytes long.

        Parameters:
        bytecode: bytecode to check

        Return:
        If the bytecode is four bytes, return it.  Else, return None.
        """
        logger.debug(f"{bytecode=}")
        if len(bytecode) != 4:
            logger.error(f"Bytecode should be 4 bytes, is {len(bytecode)}")
            return None
        return bytecode


    def _increment_offset(self) -> None:
        self.offset += 4


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

        self._increment_offset()
        return self._check_len(bytecode)


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

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_ldm(self, tokens: [str]) -> bytes:
        """
        Assemble an LDBM or LDM instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b""
        opcode = tokens[0]
        match opcode:
            case "LDM": bytecode = b"\x02"
            case "LDBM": bytecode = b"\x03"
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
        address: bytes = b""
        if tokens[2].startswith("["): # register indirect addressing
            reg_num = self.parse_register_indirect(tokens[2])
            bytecode += reg_num.to_bytes(2, byteorder='big')
        else:                   # direct address
            try:
                address = self.parse_address(tokens[2])
            except ValueError as e:
                logger.error(e)
                return None
            except Exception as e:
                logger.error("Unexpected error:", e)
                return None
            bytecode += address

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_st(self, tokens: [str]) -> bytes:
        """
        Assemble an ST* instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b""
        opcode: str = tokens[0]
        match opcode:
            case "ST": bytecode = b"\x10"
            case "STH": bytecode = b"\x11"
            case "STL": bytecode = b"\x12"
            case _:
                logger.error(f"Unimplemented or invalid instruction {opcode}")
                return None
        src_reg: int = -1
        try:
            src_reg = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += src_reg.to_bytes(1, byteorder='big')
        address: bytes = b""
        if tokens[2].startswith("["): # register indirect addressing
            reg_num = self.parse_register_indirect(tokens[2])
            bytecode += reg_num.to_bytes(2, byteorder='big')
        else:                   # direct address
            try:
                address = self.parse_address(tokens[2])
            except ValueError as e:
                logger.error(e)
                return None
            except Exception as e:
                logger.error("Unexpected error:", e)
                return None
            bytecode += address
        address: bytes = b""

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_cmr(self, tokens: [str]) -> bytes:
        """
        Assemble a CMR instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b"\x20"
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

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_cmi(self, tokens: [str]) -> bytes:
        """
        Assemble a CMI instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b"\x21"
        register: int = -1
        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += register.to_bytes(1, byteorder='big')
        word: bytes = None
        try:
            word = self.parse_int(tokens[2])
        except ValueError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error("Unexpected error:", e)
            return None
        bytecode += word

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_jump(self, tokens: [str]) -> bytes:
        """
        Assemble a jump instruction.

        All jumps have the same syntax: opcode <unused> addr, so we only need to
        vary the opcode that goes into the bytecode, which is good, because
        there are six different jump instructions in the instruction set.

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = None

        opcode: str = tokens[0]

        match opcode:
            case "JZ": bytecode = b"\x30"
            case "JNZ": bytecode = b"\x31"
            case "JC": bytecode = b"\x32"
            case "JNC": bytecode = b"\x33"
            case "JN": bytecode = b"\x34"
            case "JP": bytecode = b"\x35"
            case "JV": bytecode = b"\x36"
            case "JNV": bytecode = b"\x37"
            case "JMP": bytecode = b"\x38"
            case "JSR": bytecode = b"\x39"
            case _:
                logger.error(f"Unknown or unimplemented opcode {opcode}")
                return None

        bytecode += b"\x00"     # second byte unused

        address: bytes = None

        # see if it's a label
        label = self.parse_label([tokens[1]])
        if label is not None:
            offset = self.get_label_offset(label)
            if offset is not None:
                address = offset.to_bytes(2, byteorder='big')
        if address is None:
            try:
                address = self.parse_address(tokens[1])
            except ValueError as e:
                logger.error(e)
                return None
            except Exception as e:
                logger.error("Unexpected error:", e)
                return None
        # stack space may not be interpreted as executable code --- bad idea
        # anyways
        addr_as_int = address[0] << 8 | address[1]
        if addr_as_int < defs.STACK_MIN:
            logger.error("Programs may not jump into stack space "
                         f"([0x{defs.STACK_MAX:04x}, "
                         f"0x{defs.STACK_MIN:04x}])")
            return None
        # all instructions are four-byte aligned; jumping to a misaligned
        # address is sure to cause bugs
        if addr_as_int % 4 != 0:
            logger.error(f"Address 0x{addr_as_int:04x} not 4-byte aligned")
            return None
        bytecode += address

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_addi(self, tokens: [str]) -> bytes:
        """
        Assemble an ADDI instruction.

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\x40"

        register: int = None
        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += register.to_bytes(1, byteorder='big')

        word: bytes = None
        try:
            word = self.parse_int(tokens[2])
        except ValueError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += word

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_addr(self, tokens: [str]) -> bytes:
        """
        Assemble an ADDR instruction.

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\x41"
        dest_reg: int = -1
        try:
            dest_reg = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
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
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += src_reg.to_bytes(1, byteorder='big')
        bytecode += b"\x00"     # fourth byte unused

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_inc(self, tokens: [str]) -> bytes:
        """
        Assemble an INC instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\x42"
        register: int = -1

        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += register.to_bytes(1, byteorder='big')

        bytecode += b"\x00\x00" # unused bytes

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_subi(self, tokens: [str]) -> bytes:
        """
        Assemble a SUBI instruction.

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None
        """
        bytecode: bytes = b"\x43"

        register: int = -1
        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += register.to_bytes(1, byteorder='big')

        word: bytes = None
        try:
            word = self.parse_int(tokens[2])
        except ValueError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += word

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_subr(self, tokens: [str]) -> bytes:
        """
        Assemble a SUBR instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\x44"
        dest_reg: int = -1
        try:
            dest_reg = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
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
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += src_reg.to_bytes(1, byteorder='big')
        bytecode += b"\x00"

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_dec(self, tokens: [str]) -> bytes:
        """
        Assemble a DEC instruction

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\x45"

        register: int = -1
        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += register.to_bytes(1, byteorder='big')
        bytecode += b"\x00\x00" # bytes 3 and 4 unused

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_push(self, tokens: [str]) -> bytes:
        """
        Assemble a PUSH instruction.

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\xe0"
        register: int = -1
        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += register.to_bytes(1, byteorder='big')
        bytecode += b"\x00\x00"

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_pop(self, tokens: [str]) -> bytes:
        """
        Assemble a POP instruction.

        Parameters:
        tokens: the line to be assembled

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        bytecode: bytes = b"\xe1"
        register: int = -1
        try:
            register = self.parse_register_name(tokens[1])
        except (ac_exc.InvalidRegisterNameError,
                ac_exc.RegisterNameMissingPrefixError) as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        bytecode += register.to_bytes(1, byteorder='big')
        bytecode += b"\x00\x00"

        self._increment_offset()
        return self._check_len(bytecode)


    def _assemble_rts(self, tokens: [str]) -> bytes:
        bytecode = b"\xe2\x00\x00\x00"
        return self._check_len(bytecode)


    def _assemble_halt(self):
        bytecode: bytes = b"\xfe\xff\xfe\xff"
        self._increment_offset()
        return bytecode


    def _assemble_nop(self):
        bytecode: bytes = b"\xff\xff\xff\xff"
        self._increment_offset()
        return bytecode


    def find_labels(self, infile: typing.TextIO) -> bool:
        """
        Find source labels and populate the assembler's label dictionary.

        Parameters:
        infile: the file object associated with the source code file

        Return:
        If all labels are valid and unique, return True.  Otherwise, return
        False
        """
        self.lineno = 0
        self.offset = defs.CODE_START
        for line in infile:
            self.lineno += 1
            label: str = ""
            tokens: [str] = self.tokenize_line(line)
            # blank line
            if tokens is None or tokens[0] == ";":
                continue
            if len(tokens) == 1 and tokens[0].endswith(":"):
                label = self.parse_label([tokens[0]])
                if label is None:
                    logger.error(f"Could not parse label from {tokens}")
                    return False

                existing_offset = self.get_label_offset(label)
                if existing_offset is not None:
                    logger.error(f"Label '{label}' already defined")
                    return False
                self.add_label(label)
            else:
                self._increment_offset()
        
        return True


    def assemble(self, infile: typing.TextIO) -> bytes:
        """
        Assemble a binary from source code.

        Parameters:
        infile: the file object associated with the source code file

        Return:
        On success, return the assembled bytecode.  On failure, return None.
        """
        infile.seek(0)          # reset file position after label search
        self.lineno = 0
        self.offset = defs.CODE_START # reset offset
        bytecode: bytes = b""
        next_line: bytes = None # next assembled bytecode
        for source_line in infile:
            self.lineno += 1
            tokens = self.tokenize_line(source_line)
            if tokens is None:  # empty line, go on to the next one
                continue
            logger.debug(f"tokens: {tokens}")
            opcode: str = tokens[0]
            logger.debug(f"opcode: {opcode}")
            match opcode:
                case "LDI": next_line = self._assemble_ldi(tokens)
                case "LDR": next_line = self._assemble_ldr(tokens)
                case "LDM": next_line = self._assemble_ldm(tokens)
                case "ST" | "STH" | "STL": next_line = self._assemble_st(tokens)
                case "CMR": next_line = self._assemble_cmr(tokens)
                case "CMI": next_line = self._assemble_cmi(tokens)
                case "JZ" | "JNZ" | "JC" | "JNC" | "JN" | "JP" | "JV" | "JNV"\
                    | "JMP" | "JSR":
                    next_line = self._assemble_jump(tokens)
                case "ADDI": next_line = self._assemble_addi(tokens)
                case "ADDR": next_line = self._assemble_addr(tokens)
                case "INC": next_line = self._assemble_inc(tokens)
                case "SUBI": next_line = self._assemble_subi(tokens)
                case "SUBR": next_line = self._assemble_subr(tokens)
                case "DEC": next_line = self._assemble_dec(tokens)
                case "PUSH": next_line = self._assemble_push(tokens)
                case "POP": next_line = self._assemble_pop(tokens)
                case "RTS": next_line = self._assemble_rts(tokens)
                case "HALT": next_line = self._assemble_halt()
                case "NOP": next_line = self._assemble_nop()
                case ";":       # comment; do nothing
                    continue
                case _:
                    # this has to be here, since HALT is a valid instruction
                    # that exists by itself on a source line (len(tokens) is 1)
                    if len(tokens) == 1: # possibly a label
                        label = self.parse_label(tokens)
                        if label is None:
                            logger.error(f"Failed to parse label from {tokens}")
                            return None
                         # was a label, but this is covered by find_labels()
                        continue
                    else:
                        msg = f"Unknown or unimplemented instruction {opcode}"
                        logger.error(msg)
            if next_line is None:
                logger.error(f"Failed to assemble {opcode}")
                return None
            bytecode += next_line
            logger.debug(f"self.offset=0x{self.offset:04x}")

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
    format = "[%(levelname)s] %(name)s:%(funcName)s():%(lineno)d: %(message)s"
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
        ok = assembler.find_labels(f)
        if ok:
            bytecode: bytes = assembler.assemble(f)
            if bytecode is not None:
                f2.write(bytecode)


if __name__ == "__main__":
    main()
