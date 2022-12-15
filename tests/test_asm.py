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
