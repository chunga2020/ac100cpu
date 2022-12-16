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
