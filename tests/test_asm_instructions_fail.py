import pathlib

import src.ac100asm as asm

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_failing")
ldi_tests = pathlib.Path(test_srcd, "ldi_tests")
ldr_tests = pathlib.Path(test_srcd, "ldr_tests")
ldm_tests = pathlib.Path(test_srcd, "ldm_tests")
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

    def test_ldi_decimal_too_negative(self):
        source_file = pathlib.Path(ldi_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail when decimal is too negative"

    def test_ldi_decimal_too_big(self):
        source_file = pathlib.Path(ldi_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail when decimal is too large"

    def test_ldi_hex_missing_prefix(self):
        source_file = pathlib.Path(ldi_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail when hex word is missing prefix"

    def test_ldi_hex_three_hexits(self):
        source_file = pathlib.Path(ldi_tests, "test06")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex value has 3 hexits"

    def test_ldi_hex_too_big(self):
        source_file = pathlib.Path(ldi_tests, "test07")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex value larger than 2 bytes"

    def test_ldi_hex_invalid_hexits(self):
        source_file = pathlib.Path(ldi_tests, "test08")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex value contains non-hex digits"

    def test_ldi_binary_too_wide(self):
        source_file = pathlib.Path(ldi_tests, "test09")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if binary value is larger than 16 bits"

    def test_ldi_binary_invalid_bits(self):
        source_file = pathlib.Path(ldi_tests, "test10")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if 'binary' value has non-binary digits"


class TestLdrFailures:
    def test_ldr_bad_destination_register(self):
        source_file = pathlib.Path(ldr_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if LDR has a bad destination register"

    def test_ldr_dest_reg_missing_prefix(self):
        source_file = pathlib.Path(ldr_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if dest register missing prefix"

    def test_ldr_source_register_too_small(self):
        source_file = pathlib.Path(ldr_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register < 1"

    def test_ldr_source_register_too_big(self):
        source_file = pathlib.Path(ldr_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register > 16"

    def test_ldr_source_register_missing_prefix(self):
        source_file = pathlib.Path(ldr_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register missing prefix"


class TestLdmFailures:
    def test_ldm_dest_register_too_small(self):
        source_file = pathlib.Path(ldm_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "LDM assembly should fail if destination reg < 1"

    def test_ldm_dest_register_too_big(self):
        source_file = pathlib.Path(ldm_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "LDM assembly should fail if destination reg > 16"

    def test_ldm_dest_register_missing_prefix(self):
        source_file = pathlib.Path(ldm_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "LDM assembly should fail if destination reg missing prefix"


class TestStFailures:
    def test_st_source_register_too_small(self):
        source_file = pathlib.Path(st_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register < 1"

    def test_st_source_register_too_big(self):
        source_file = pathlib.Path(st_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register > 16"

    def test_st_source_register_missing_prefix(self):
        source_file = pathlib.Path(st_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if source register is missing prefix"

    def test_st_destination_address_missing_prefix(self):
        source_file = pathlib.Path(st_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if address is missing hex prefix"

    def test_st_destination_address_too_small(self):
        source_file = pathlib.Path(st_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "Assembly should fail if hex address not 16 bits wide"

    def test_st_destination_address_too_big(self):
        source_file = pathlib.Path(st_tests, "test06")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "ST assembly should fail if hex address > 16 bits wide"
