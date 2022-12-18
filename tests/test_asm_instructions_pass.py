import os
import pathlib

import src.ac100asm as asm

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_passing")

class TestAssemblerPasses:
    def test_ignores_whitespace(self):
        source_file = pathlib.Path(test_srcd, "test01")
        with open(source_file, "r") as f:
            expected = b""
            bytecode = assembler.assemble(f)
            assert bytecode == expected, "Failed to ignore whitespace"
            assert assembler.lineno == 1, "Expected assembler to be on line 1"

    def test_ignores_single_comment(self):
        source_file = pathlib.Path(test_srcd, "test02")
        with open(source_file, "r") as f:
            expected = b""
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 1, "Expected assembler to be on line 1"
            assert bytecode == expected,\
                "Assembler did not successfully ignore a one-line comment"

    def test_ignores_multiple_comments(self):
        source_file = pathlib.Path(test_srcd, "test03")
        with open(source_file, "r") as f:
            expected = b""
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected,\
                "Assembler did not ignore multiple comment lines"

    def test_ldi_halt(self):
        source_file = pathlib.Path(test_srcd, "test04")
        expected = b"\x00\x00\x00\x01" # byte 2 is 0, since we decrement regs
        expected += b"\xfe\xff\xfe\xff"
        outfile = pathlib.Path(test_srcd, "assembles_ldi_halt.bin")
        with open(source_file, "r") as f, open(outfile, "wb") as f2:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 2, "Expected assembler to be on line 2"
            assert bytecode == expected,\
                "Assembler did not assemble LDI and HALT"
            f2.write(bytecode)
        assert os.stat(outfile).st_size\
            == len(expected)

    def test_ldr(self):
        source_file = pathlib.Path(test_srcd, "test05")
        expected = b"\x00\x00\x00\x05"
        expected += b"\x01\x01\x00\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected,\
                "Assembler did not assemble LDR"

    def test_ldm(self):
        source_file = pathlib.Path(test_srcd, "test07")
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x10\x00\x05\x00"
        expected += b"\x02\x01\x05\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 4, "Expected assembler to be on line 4"
            assert bytecode == expected, "Assembler did not assemble LDM"

    def test_st(self):
        source_file = pathlib.Path(test_srcd, "test06")
        expected = b"\x00\x00\xde\xad"
        expected += b"\x10\x00\xbe\xef"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected,\
                "Assembler did not assemble ST"

    def test_sth(self):
        source_file = pathlib.Path(test_srcd, "test08")
        expected = b"\x00\x00\x00\x02"
        expected += b"\x11\x00\x02\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, "Assembler did not assemble STH"

    def test_stl(self):
        source_file = pathlib.Path(test_srcd, "test09")
        expected = b"\x00\x00\x00\x02"
        expected += b"\x12\x00\x05\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be on line 3"
            assert bytecode == expected, "Failed to assembled STL"

    def test_cmr(self):
        source_file = pathlib.Path(test_srcd, "test10")
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x00\x01\x00\x20"
        expected += b"\x20\x00\x01\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 4, "Expected assembler to be on line 4"
            assert bytecode == expected, "Failed to assemble CMR"

    def test_cmi(self):
        source_file = pathlib.Path(test_srcd, "test11")
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\00\x00\x20"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 3, "Expected assembler to be line 3"
            assert bytecode == expected, "Failed to assemble CMR"

    def test_je(self):
        source_file = pathlib.Path(test_srcd, "test12")
        expected = b"\x00\x00\x00\x17"
        expected += b"\x21\x00\x00\x2a"
        expected += b"\x30\x00\x03\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 4, "Expected assembler to be on line 4"
            assert bytecode == expected, "Failed to assemble JE"

    def test_jg(self):
        source_file = pathlib.Path(test_srcd, "test13")
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x20"
        expected += b"\x31\x00\x04\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 4, "Expected assembler to be on line 4"
            assert bytecode == expected, "Failed to assemble JG"

    def test_jge(self):
        source_file = pathlib.Path(test_srcd, "test14")
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x2a"
        expected += b"\x32\x00\x05\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 4, "Expected assembler to be on line 4"
            assert bytecode == expected, "Failed to assemble JGE"

    def test_jl(self):
        source_file = pathlib.Path(test_srcd, "test15")
        expected = b"\x00\x00\x00\x2a"
        expected += b"\x21\x00\x00\x54"
        expected += b"\x33\x00\x04\x00"
        expected += b"\xfe\xff\xfe\xff"
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert assembler.lineno == 4, "Expected assembler to be on line 4"
            assert bytecode == expected, "Failed to assemble JL"
