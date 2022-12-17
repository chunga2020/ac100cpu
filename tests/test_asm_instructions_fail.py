import pathlib

import src.ac100asm as asm

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_failing")
ldi_tests = pathlib.Path(test_srcd, "ldi_tests")
ldr_tests = pathlib.Path(test_srcd, "ldr_tests")
st_tests = pathlib.Path(test_srcd, "st_tests")

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

        source_file = pathlib.Path(ldi_tests, "test08")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex value contains non-hex digits"

    def test_ldi_invalid_binary(self):
        source_file = pathlib.Path(ldi_tests, "test09")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if binary value is larger than 16 bits"

        source_file = pathlib.Path(ldi_tests, "test10")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if 'binary' value has non-binary digits"


class TestLdrFailures:
    def test_bad_destination_register(self):
        source_file = pathlib.Path(ldr_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if LDR has a bad destination register"

        source_file = pathlib.Path(ldr_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if dest register missing prefix"

    def test_bad_source_register(self):
        source_file = pathlib.Path(ldr_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register < 1"

        source_file = pathlib.Path(ldr_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register > 16"

        source_file = pathlib.Path(ldr_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register missing prefix"


class TestStFailures:
    def test_bad_source_register(self):
        source_file = pathlib.Path(st_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register < 0"

        source_file = pathlib.Path(st_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register > 16"

        source_file = pathlib.Path(st_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register is missing prefix"

    def test_bad_destination_address(self):
        source_file = pathlib.Path(st_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if address is missing hex prefix"

        source_file = pathlib.Path(st_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex address not 16 bits wide"

        source_file = pathlib.Path(st_tests, "test06")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "ST assembly should fail if hex address > 16 bits wide"
