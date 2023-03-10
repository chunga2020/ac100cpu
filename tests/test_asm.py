import pathlib
import pytest

import src.definitions as defs
import src.exceptions as ac_exc
import src.ac100asm as asm

@pytest.fixture
def assembler():
    return asm.AC100ASM()

test_srcd = pathlib.Path("asm_tests_passing")

class TestAssembler:
    def test_tokenize_line(self, assembler):
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


class TestParseLabel:
    @pytest.mark.parametrize("ltext, fail_msg",
        [
            ("test:", "Failed to parse lowercase-only label"),
            ("test123:", "Failed to parse lower, digit-only label"),
            ("TEST:", "Failed to parse uppercase-only label"),
            ("TEST123:", "Failed to parse upper, digit-only"),
            ("testTEST:", "Failed to parse upper,lower-only label"),
            ("test_Something42:", "Failed to parse lower,underscore,any label")
        ])
    def test_valid_label(self, assembler, ltext, fail_msg):
        label = assembler.parse_label([ltext])
        assert label == ltext[:len(ltext)-1], fail_msg

    @pytest.mark.parametrize("ltext, fail_msg",
        [
            ("_:", "Lone single underscores are not valid labels"),
            ("___:", "underscore-only identifiers are not valid labels"),
            ("_test:", "Leading single underscores are not valid"),
            ("___test:", "Multiple leading underscores are not valid"),
            ("1:", "Labels may not begin with a digit"),
            ("123:", "Labels may not begin with a digit"),
            ("123_test:", "Labels may not begin with a digit")
        ])
    def test_invalid_label(self, assembler, ltext, fail_msg):
        rv = assembler.parse_label([ltext])
        assert not rv, fail_msg

    @pytest.mark.parametrize("src_file, expected_map",
        [
            ("label_test01", {"start": 0x0200}),
            ("label_test02", {"start": 0x0200, "loop": 0x0204, "done": 0x214})
        ])
    def test_label_in_file(self, assembler, src_file, expected_map):
        with open(pathlib.Path(test_srcd, src_file), "r") as f:
            ok = assembler.find_labels(f)
            assert ok and assembler.labels == expected_map

class TestParseRegisterName:
    @pytest.mark.parametrize("name, expected", [("R1", 0), ("R2", 1), ("R3", 2),
                            ("R4", 3), ("R5", 4), ("R6", 5), ("R7", 6),
                            ("R8", 7), ("R9", 8), ("R10", 9), ("R11", 10),
                            ("R12", 11), ("R13", 12), ("R14", 13), ("R15", 14),
                            ("R16", 15)])
    def test_valid_register(self, assembler, name, expected):
        parsed = assembler.parse_register_name(name)
        assert parsed == expected, f"Got value {parsed} while parsing {name}, "\
            f"but expected {expected}"

    def test_no_register_prefix(self, assembler):
        token = "1"             # valid number, but no prefix
        with pytest.raises(ac_exc.RegisterNameMissingPrefixError):
            assembler.parse_register_name(token)

    def test_register_name_too_low(self, assembler):
        token = "R0"
        with pytest.raises(ac_exc.InvalidRegisterNameError):
            assembler.parse_register_name(token)

    def test_register_name_too_high(self, assembler):
        token = "R20"
        with pytest.raises(ac_exc.InvalidRegisterNameError):
            assembler.parse_register_name(token)


class TestParseRegisterIndirect:
    @pytest.mark.parametrize("token, number",
    [
        ("[R1]", 0), ("[R2]", 1), ("[R3]", 2), ("[R4]", 3), ("[R5]", 4),
        ("[R6]", 5), ("[R7]", 6), ("[R8]", 7), ("[R9]", 8), ("[R10]", 9),
        ("[R11]", 10), ("[R12]", 11), ("[R13]", 12), ("[R14]", 13),
        ("[R15]", 14), ("[R16]", 15)
    ])
    def test_parse_indirect_ok(self, assembler, token, number):
        result = assembler.parse_register_indirect(token)
        assert result == number


class TestParseInt:
    def test_decimal(self, assembler):
        token = "-65536"        # too negative for 16 bits
        with pytest.raises(ValueError):
            assembler.parse_int(token)

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
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        token = "5.5"           # floats not supported
        with pytest.raises(ValueError):
            assembler.parse_int(token)

    @pytest.mark.parametrize("token, expected",
                             [("0x0", b"\x00\x00"), ("0xf3", b"\x00\xf3"),
                              ("0x0000", b"\x00\x00"), ("0xffff", b"\xff\xff")])
    def test_valid_hex(self, assembler, token, expected):

        number = assembler.parse_int(token)
        assert number == expected,\
            f"Should have gotten {expected} on token {token}, but got "\
            f"{number}"

    def test_invalid_hex(self, assembler):
        token = "0xg"           # invalid hex digit
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        token = "0x000"         # can???t make bytes out of odd number of hexits
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
    def test_valid_binary(self, assembler, token, expected):
        number = assembler.parse_int(token)
        assert number == expected, f"Expected {expected} for token {token}, "\
            f"but got {number}"

    def test_invalid_binary(self, assembler):
        token = "0b"
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        # 0b0 00000000 00000000
        token = "0b00000000000000000" # valid zero, but too many bits (17)
        with pytest.raises(ValueError):
            assembler.parse_int(token)

        # 0b1 11111111 11111111
        token = "0b11111111111111111" # too big for 16 bits
        with pytest.raises(ValueError):
            assembler.parse_int(token)


class TestParseAddress:
    @pytest.mark.parametrize("token, expected",
                             [("0x0000", b"\x00\x00"), ("0xffff", b"\xff\xff"),
                              ("0xbeef", b"\xbe\xef"), ("0xdead", b"\xde\xad")])
    def test_valid_address(self, assembler, token, expected):
        address = assembler.parse_address(token)
        assert address == expected, f"Expected {expected} for token "\
            f"'{token}', but got {address}"

    def test_invalid_address(self, assembler):
        # valid hex number, but missing prefix, so would be interpreted as
        # decimal, which we???re disallowing
        token = "1234"
        with pytest.raises(ValueError):
            assembler.parse_address(token)

        token = "0x000000"      # valid hex number, but too big (24 bits)
        with pytest.raises(ValueError):
            assembler.parse_address(token)

        token = "0xghij"        # right length, invalid hex
        with pytest.raises(ValueError):
            assembler.parse_address(token)

        # addresses can???t be given in binary (why would you want to do this?!)
        token = "0b10101010"
        with pytest.raises(ValueError):
            assembler.parse_address(token)
