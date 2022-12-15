import pytest

import src.definitions as defs
import src.exceptions as ac_exc
import src.ac100asm as asm

assembler = asm.AC100ASM()

class TestAssembler:
    def test_tokenize_line(self):
        line = ""
        result = assembler.tokenize_line(line)
        assert result is None,\
            "Should have gotten None when tokenizing empty string"
        line = "    "
        result = assembler.tokenize_line(line)
        assert result is None,\
            "Should have gotten None when tokenizing whitespace-only string"
        line = "LDI R1 1"
        expected = ["LDI", "R1", "1"]
        result = assembler.tokenize_line(line)
        assert result == expected, f"Should have gotten {expected} when "\
            f"tokenizing '{line}', but got {result}"


class TestParseRegisterName:
    @pytest.mark.parametrize("name, expected", [("R1", 0), ("R2", 1), ("R3", 2),
                            ("R4", 3), ("R5", 4), ("R6", 5), ("R7", 6),
                            ("R8", 7), ("R9", 8), ("R10", 9), ("R11", 10),
                            ("R12", 11), ("R13", 12), ("R14", 13), ("R15", 14),
                            ("R16", 15)])
    def test_valid_register(self, name, expected):
        parsed = assembler.parse_register_name(name)
        assert parsed == expected, f"Got value {parsed} while parsing {name}, "\
            f"but expected {expected}"

    def test_no_register_prefix(self):
        token = "1"             # valid number, but no prefix
        with pytest.raises(ac_exc.RegisterNameMissingPrefixError):
            assembler.parse_register_name(token)

    def test_register_name_too_low(self):
        token = "R0"
        with pytest.raises(ac_exc.InvalidRegisterNameError):
            assembler.parse_register_name(token)

    def test_register_name_too_high(self):
        token = "R20"
        with pytest.raises(ac_exc.InvalidRegisterNameError):
            assembler.parse_register_name(token)


class TestParseInt:
    def test_decimal(self):
        token = "-65536"        # too negative for 16 bits
        number = assembler.parse_int(token)
        assert number is None, "Should have failed on too-negative value "\
            f"'{token}'"

        token = "-1"            # OK
        number = assembler.parse_int(token)
        expected = b"\xff\xff"
        assert number == expected, f"Expected {expected} for '{token}', but got "\
            f"{number}"

        token = "23"            # OK
        expected = b"\x00\x17"
        number = assembler.parse_int(token)
        assert number == expected, f"Expected {expected} for '{token}', but got "\
            f"{number}"

        token = "65537"         # too big for 16 bits
        number = assembler.parse_int(token)
        assert number is None, "Should have failed on too-large number "\
            f"'{token}'"

        token = "5.5"           # OK, but truncates
        number = assembler.parse_int(token)
        expected = 5
        assert number is None, f"Should have gotten failed on "\
            f"'{token}', but got {number}"

    @pytest.mark.parametrize("token, expected",
                             [("0x0", b"\x00"), ("0xf3", b"\xf3"),
                              ("0x0000", b"\x00\x00"), ("0xffff", b"\xff\xff")])
    def test_valid_hex(self, token, expected):

        number = assembler.parse_int(token)
        assert number == expected,\
            f"Should have gotten {expected} on token {token}, but got "\
            f"{number}"

    def test_invalid_hex(self):
        token = "0xg"           # invalid hex digit
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        token = "0x000"         # can’t make bytes out of odd number of hexits
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        token = "0x00000000"    # 32 bits -- too big!
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        token = "0xffffffff"    # 32 bits -- too big
        with pytest.raises(ValueError):
            assembler.parse_int(token)

    @pytest.mark.parametrize("token, expected",
                             [("0b0", b"\x00\x00"), ("0b01010101", b"\x00\x55"),
                              ("0b00000000", b"\x00\x00"),
                              ("0b11111111", b"\x00\xff"),
                              ("0b0000000000000000", b"\x00\x00"),
                              ("0b1111111111111111", b"\xff\xff")])
    def test_valid_binary(self, token, expected):
        number = assembler.parse_int(token)
        assert number == expected, f"Expected {expected} for token {token}, "\
            f"but got {number}"

    def test_invalid_binary(self):
        token = "0b"
        with pytest.raises(ValueError):
            number = assembler.parse_int(token)

        # 0b0 00000000 00000000
        token = "0b00000000000000000" # valid zero, but too many bits (17)
        with pytest.raises(ValueError):
            number = assembler.parse_int(token)

        # 0b1 11111111 11111111
        token = "0b11111111111111111" # too big for 16 bits
        with pytest.raises(ValueError):
            number = assembler.parse_int(token)


class TestParseAddress:
    @pytest.mark.parametrize("token, expected",
                             [("0x0000", b"\x00\x00"), ("0xffff", b"\xff\xff"),
                              ("0xbeef", b"\xbe\xef"), ("0xdead", b"\xde\xad")])
    def test_valid_address(self, token, expected):
        address = assembler.parse_address(token)
        assert address == expected, f"Expected {expected} for token "\
            f"'{token}', but got {address}"

    def test_invalid_address(self):
        # valid hex number, but missing prefix, so would be interpreted as
        # decimal, which we’re disallowing
        token = "1234"
        with pytest.raises(ValueError):
            address = assembler.parse_address(token)

        token = "0x000000"      # valid hex number, but too big (24 bits)
        with pytest.raises(ValueError):
            address = assembler.parse_address(token)

        token = "0xghij"        # right length, invalid hex
        with pytest.raises(ValueError):
            assembler.parse_address(token)

        # addresses can’t be given in binary (why would you want to do this?!)
        token = "0b10101010"
        with pytest.raises(ValueError):
            address = assembler.parse_address(token)
