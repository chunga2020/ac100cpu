import pathlib
import pytest

import src.ac100asm as asm
import src.exceptions as ac_exc

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_failing")
ldi_tests = pathlib.Path(test_srcd, "ldi_tests")

class TestLdiFailures:
    def test_ldi_bad_register(self):
        source_file = pathlib.Path(ldi_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should have failed with bad register name"

    def test_ldi_register_no_prefix(self):
        source_file = pathlib.Path(ldi_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should have failed with register without prefix"

    def test_ldi_invalid_decimal(self):
        source_file = pathlib.Path(ldi_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail when decimal is too negative"

        source_file = pathlib.Path(ldi_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail when decimal is too large"

    def test_ldi_invalid_hex(self):
        source_file = pathlib.Path(ldi_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail when hex word is missing prefix"

        source_file = pathlib.Path(ldi_tests, "test06")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex value has 3 hexits"

        source_file = pathlib.Path(ldi_tests, "test07")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex value larger than 2 bytes"
