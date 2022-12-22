import pathlib
import pytest

import src.ac100asm as asm

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_passing")

class TestAssemblerPasses:
    @pytest.mark.parametrize("name, expected, lineno, offset, fail_msg",
        [
            ("whitespace-test01", b"", 1, 0x200, "Didn't ignore whitespace"),
            ("single-line-comment-test01", b"", 1, 0x200,
             "Didn't ignore single comment"),
            ("multiple-comments-test01", b"", 3, 0x200,
             "Didn't ignore comment block"),
            ("halt-test01", b"\xfe\xff\xfe\xff", 1, 0x204,
             "Didn't assemble HALT"),
            ("ldi-test-decimal01", b"\x00\x00\x00\x01", 1, 0x204,
             "LDI assembly with midrange decimal integer failed"),
            ("ldi-test-decimal02", b"\x00\x00\x80\00", 1, 0x204,
             "LDI assembly with most negative 16-bit decimal integer failed"),
            ("ldi-test-decimal03", b"\x00\x00\xff\xff", 1, 0x204,
             "LDI assembly with most positive 16-bit decimal integer failed"),
            ("ldi-test-hex01", b"\x00\x00\x00\x00", 1, 0x204,
             "LDI assembly with minimum 16-bit hex integer failed"),
            ("ldi-test-hex02", b"\x00\x00\xff\xff", 1, 0x204,
             "LDI assembly with maximum 16-bit hex integer failed"),
            ("ldi-test-hex03", b"\x00\x00\x07\x28", 1, 0x204,
             "LDI assembly with midrange 16-bit hex integer failed"),
            ("ldi-test-binary01", b"\x00\x00\x00\x00", 1, 0x204,
             "LDI assembly with 16-bit binary zero failed"),
            ("ldi-test-binary02", b"\x00\x00\x00\x00", 1, 0x204,
             "LDI assembly with 8-bit binary zero failed"),
            ("ldi-test-binary03", b"\x00\x00\xff\xff", 1, 0x204,
             "LDI assembly with maximum 16-bit binary integer failed"),
            ("ldi-test-binary04", b"\x00\x00\x00\xff", 1, 0x204,
             "LDI assembly with midrange 8-bit binary integer failed"),
            ("ldi-test-binary05", b"\x00\x00\xaa\xaa", 1, 0x204,
             "LDI assembly with midrange 16-bit binary integer failed"),
            ("ldr-test01", b"\x00\x00\x00\x05\x01\x01\x00\x00", 2, 0x208,
             "LDR assembly with midrange decimal integer failed"),
            ("ldm-test01", b"\x00\x00\x00\x2a\x10\x00\x05\x00\x02\x01\x05\x00",
             3, 0x20c, "LDM assembly with a midrange decimal integer failed"),
            ("st-test01", b"\x00\x00\xde\xad\x10\x00\xbe\xef", 2, 0x208,
             "ST assembly with a midrange hex integer failed"),
            ("sth-test-decimal01", b"\x00\x00\x00\x02\x11\x00\x02\x00", 2,
             0x208, "STH assembly with a midrange decimal integer failed"),
            ("stl-test-decimal01", b"\x00\x00\x00\x02\x12\x00\x05\x00", 2,
             0x208, "STL assembly with a midrange decimal integer failed"),
            ("cmr-test01", b"\x00\x00\x00\x2a\x00\x01\x00\x20\x20\x00\x01\x00",
             3, 0x20c, "CMR assembly with two midrange decimal integers failed"),
            ("cmi-decimal-decimal-test01", b"\x00\x00\x00\x2a\x21\00\x00\x20",
             2, 0x208, "CMI assembly with two midrange decimal integers failed"),
            ("je-decimal-decimal-test01",
             b"\x00\x00\x00\x17\x21\x00\x00\x2a\x30\x00\x03\x00", 3, 0x20c,
             "JE assembly with two midrange decimal integers failed"),
            ("jg-decimal-decimal-test01",
             b"\x00\x00\x00\x2a\x21\x00\x00\x20\x31\x00\x04\x00", 3, 0x20c,
             "JG assembly with two midrange decimal integers failed"),
            ("jge-decimal-decimal-test01",
             b"\x00\x00\x00\x2a\x21\x00\x00\x2a\x32\x00\x05\x00", 3, 0x20c,
             "JGE assembly with two midrange decimal integers failed"),
            ("jl-decimal-decimal-test01",
             b"\x00\x00\x00\x2a\x21\x00\x00\x54\x33\x00\x04\x00", 3, 0x20c,
             "JL assembly with two midrange integers failed"),
            ("jle-decimal-decimal-test01",
             b"\x00\x00\x00\x2a\x21\x00\x00\x54\x34\x00\x05\x00", 3, 0x20c,
             "JLE assembly with two midrange decimal integers failed"),
            ("jmp-test01", b"\x00\x00\x00\x2a\x35\x00\x05\x00", 2, 0x208,
             "JMP assembly with decimal integer failed"),
            ("addi-decimal-decimal-test01", b"\x00\x00\x00\x14\x40\x00\x00\x14",
             2, 0x208, "ADDI assembly with two midrange decimal integers failed"),
            ("addr-decimal-decimal-test01",
             b"\x00\x00\x00\x2a\x00\x01\x00\x0a\x41\x00\x01\x00", 3, 0x20c,
             "ADDR assembly with two midrange decimal integers failed"),
            ("inc-decimal-test01", b"\x00\x00\x00\x2a\x42\x00\x00\x00", 2, 0x208,
             "INC assembly with midrange decimal integer failed"),
            ("subi-decimal-decimal-test01", b"\x00\x00\x00\x2a\x43\x00\x00\x15",
             2, 0x208, "SUBI assembly with two midrange decimal integers failed"),
            ("subr-decimal-decimal-test01",
             b"\x00\x00\x00\x2a\x00\x01\x00\x15\x44\x00\x01\x00", 3, 0x20c,
             "SUBR assembly with two midrange decimal integers failed"),
            ("dec-decimal-test01", b"\x00\x00\x00\x2a\x45\x00\x00\x00", 2, 0x208,
             "DEC assembly with decimal integer failed"),
            ("push-decimal-test01", b"\x00\x00\x00\x2a\xe0\x00\x00\x00", 2, 0x208,
             "PUSH assembly with midrange decimal integer failed"),
            ("pop-decimal-test01",
             b"\x00\x00\x00\x2a\xe0\x00\x00\x00\xe1\x01\x00\x00", 3, 0x20c,
             "POP assembly failed"),
            ("nop-test01", b"\xff\xff\xff\xff", 1, 0x204, "NOP assembly failed")
        ])
    def test_instruction(self, name, expected, lineno, offset, fail_msg):
        """
        name: name of the test
        expected: the expected bytecode
        lineno: source file line number assembler is expected to be on at the
        end of the test
        offset: RAM offset assembler is expected to have at the end of the test
        fail_msg: message to print if assembled bytecode != expected
        """
        source_file = pathlib.Path(test_srcd, name)
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode == expected, fail_msg
            assert assembler.offset == offset,\
                f"Expected assembler to have offset 0x{offset:04x}"
            assert assembler.lineno == lineno,\
                f"Expected assembler to be on line {lineno}"

