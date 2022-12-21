import os
import pathlib

import src.ac100asm as asm

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_passing")

class TestAssemblerPasses:
    def test_ignores_whitespace(self):
        source_file = pathlib.Path(test_srcd, "whitespace-test01")
        with open(source_file, "r") as f:
            expected = b""
            bytecode = assembler.assemble(f)
            assert bytecode == expected, "Failed to ignore whitespace"
            assert assembler.lineno == 1, "Expected assembler to be on line 1"

    def test_ignores_single_comment(self):
        source_file = pathlib.Path(test_srcd, "single-line-comment-test01")
        with open(source_file, "r") as f:
            expected = b""
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 1, "Expected assembler to be on line 1"
            assert bytecode == expected,\
                "Assembler failed to ignore a one-line comment"

    def test_ignores_multiple_comments(self):
        source_file = pathlib.Path(test_srcd, "multiple-comments-test01")
        with open(source_file, "r") as f:
            expected = b""
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected,\
                "Assembler failed to ignore multiple comment lines"

    def test_halt_01(self):
        slug = "halt-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 1, "Expected assembler to be on line 1"
            assert bytecode == expected, f"{slug} failed"

    def test_ldi_decimal_01(self):
        slug = "ldi-test-decimal01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x01" # byte 2 is 0, since we decrement regs
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 1, "Expected assembler to be on line 1"
            assert bytecode == expected, f"{slug} failed"

    def test_ldr(self):
        slug = "ldr-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x05"
        expected += b"\x01\x01\x00\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_ldm(self):
        slug = "ldm-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x10\x00\x05\x00"
        expected += b"\x02\x01\x05\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_st(self):
        slug = "st-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\xde\xad"
        expected += b"\x10\x00\xbe\xef"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_sth_decimal01(self):
        slug = "sth-test-decimal01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x02"
        expected += b"\x11\x00\x02\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_stl_decimal01(self):
        slug = "stl-test-decimal01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x02"
        expected += b"\x12\x00\x05\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_cmr01(self):
        slug = "cmr-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x00\x01\x00\x20"
        expected += b"\x20\x00\x01\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_cmi_decimal_decimal01(self):
        slug = "cmr-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\00\x00\x20"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_je_decimal_decimal01(self):
        slug = "je-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x17"
        expected += b"\x21\x00\x00\x2a"
        expected += b"\x30\x00\x03\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_jg_decimal_decimal01(self):
        slug = "jg-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x20"
        expected += b"\x31\x00\x04\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_jge_decimal_decimal01(self):
        slug = "jge-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x2a"
        expected += b"\x32\x00\x05\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_jl_decimal_decimal01(self):
        slug = "jl-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x54"
        expected += b"\x33\x00\x04\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_jle(self):
        slug = "jle-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x54"
        expected += b"\x34\x00\x05\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_jmp01(self):
        slug = "jmp-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x35\x00\x05\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_addi_decimal_decimal01(self):
        slug = "addi-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x14"
        expected += b"\x40\x00\x00\x14"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_addr_decimal_decimal01(self):
        slug = "addr-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x00\x01\x00\x0a"
        expected += b"\x41\x00\x01\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_inc_decimal01(self):
        slug = "inc-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x42\x00\x00\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_subi_decimal_decimal01(self):
        slug = "subi-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x43\x00\x00\x15"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"

    def test_subr_decimal_decimal01(self):
        slug = "subr-decimal-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x00\x01\x00\x15"
        expected += b"\x44\x00\x01\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, f"{slug} failed"

    def test_dec_decimal01(self):
        slug = "dec-decimal-test01"
        source_file = pathlib.Path(test_srcd, slug)
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x45\x00\x00\x00"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected, f"{slug} failed"
