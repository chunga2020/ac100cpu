import pytest

import src.definitions as defs
import src.exceptions as ac_exc
import src.ac100asm as asm

class TestAssembler:
    def test_tokenize_line(self):
        assembler = asm.AC100ASM()
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

    @pytest.mark.parametrize("name, expected", [("R1", 0), ("R2", 1), ("R3", 2),
                            ("R4", 3), ("R5", 4), ("R6", 5), ("R7", 6),
                            ("R8", 7), ("R9", 8), ("R10", 9), ("R11", 10),
                            ("R12", 11), ("R13", 12), ("R14", 13), ("R15", 14),
                            ("R16", 15)])
    def test_parse_register_name_valid(self, name, expected):
        assembler = asm.AC100ASM()
        parsed = assembler.parse_register_name(name)
        assert parsed == expected, f"Got value {parsed} while parsing {name}, "\
            f"but expected {expected}"

    def test_parse_register_name_no_prefix(self):
        assembler = asm.AC100ASM()
        token = "1"             # valid number, but no prefix
        with pytest.raises(ac_exc.RegisterNameMissingPrefixError):
            assembler.parse_register_name(token)

    def test_parse_register_name_too_low(self):
        assembler = asm.AC100ASM()
        token = "R0"
        with pytest.raises(ac_exc.InvalidRegisterNameError):
            assembler.parse_register_name(token)

    def test_parse_register_name_too_high(self):
        assembler = asm.AC100ASM()
        token = "R20"
        with pytest.raises(ac_exc.InvalidRegisterNameError):
            assembler.parse_register_name(token)

    def test_parse_int_decimal(self):
        assembler = asm.AC100ASM()
        token = "-65536"        # too negative for 16 bits
        number = assembler.parse_int(token)
        assert number is None, "Should have failed on too-negative value "\
            f"'{token}'"

        token = "-1"            # OK
        number = assembler.parse_int(token)
        assert number == -1, f"Should have gotten -1 for '{token}', but got "\
            f"{number}"

        token = "23"            # OK
        number = assembler.parse_int(token)
        assert number == 23, f"Should have gotten 23 for '{token}', but got "\
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
