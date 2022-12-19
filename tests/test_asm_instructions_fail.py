import pathlib
import pytest

import src.ac100asm as asm

assembler = asm.AC100ASM()
test_srcd = pathlib.Path("asm_tests_failing")
ldi_tests = pathlib.Path(test_srcd, "ldi_tests")
ldr_tests = pathlib.Path(test_srcd, "ldr_tests")
ldm_tests = pathlib.Path(test_srcd, "ldm_tests")
st_tests = pathlib.Path(test_srcd, "st_tests")
cmr_tests = pathlib.Path(test_srcd, "cmr_tests")
cmi_tests = pathlib.Path(test_srcd, "cmi_tests")
jump_tests = pathlib.Path(test_srcd, "jump_tests")

class TestLdiFailures:
    @pytest.mark.parametrize("src_file, assert_msg",
        [
            ("test01", "LDI assembly should fail with bad register name"),
            ("test02", "LDI assembly should fail with register without prefix"),
            ("test03", "LDI assembly should fail when decimal is too negative"),
            ("test04", "LDI assembly should fail when decimal is too large"),
            ("test05", "LDI assembly should fail when hex word is missing prefix"),
            ("test06", "LDI assembly should fail if hex value has 3 hexits"),
            ("test07", "LDI assembly should fail if hex value larger than 2 bytes"),
            ("test08", "LDI assembly should fail if hex value contains non-hex digits"),
            ("test09", "LDI assembly should fail if binary value is larger than 16 bits"),
            ("test10", "LDI assembly should fail if 'binary' value has non-binary digits")
        ])
    def test_ldi_failures(self, src_file, assert_msg):
        with open(pathlib.Path(ldi_tests, src_file), "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg


class TestLdrFailures:
    @pytest.mark.parametrize("src_file,assert_msg",
        [
            ("test01", "LDR assembly should fail with bad destination register"),
            ("test02", "LDR assembly should fail if dest register missing prefix"),
            ("test03", "LDR assembly should fail if source register < 1"),
            ("test04", "LDR assembly should fail if source register > 16"),
            ("test05", "LDR assembly should fail if source register missing prefix")
        ])
    def test_ldr_failures(self, src_file, assert_msg):
        with open(pathlib.Path(ldr_tests, src_file), "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg

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

    def test_ldm_address_decimal(self):
        source_file = pathlib.Path(ldm_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "LDM assembly should fail if source address given in decimal"

    def test_ldm_address_three_digits(self):
        source_file = pathlib.Path(ldm_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "LDM assembly should fail if hex address < 16 bits wide"


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

class TestCmrFailures:
    def test_destination_reg_missing_prefix(self):
        source_file = pathlib.Path(cmr_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMR assembly should fail if dest register missing prefix"

    def test_destination_reg_too_small(self):
        source_file = pathlib.Path(cmr_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMR assembly should fail if dest register < 1"

    def test_destination_reg_too_big(self):
        source_file = pathlib.Path(cmr_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMR assembly should fail if destination reg > 16"

    def test_source_reg_missing_prefix(self):
        source_file = pathlib.Path(cmr_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMR assembly should fail if source register missing prefix"

    def test_source_reg_too_small(self):
        source_file = pathlib.Path(cmr_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMR assembly should fail if source register < 1"

    def test_source_reg_too_big(self):
        source_file = pathlib.Path(cmr_tests, "test06")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMR assembly should fail if source reg > 16"

class TestCmiFailures:
    def test_register_too_small(self):
        source_file = pathlib.Path(cmi_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if register < 1"

    def test_register_too_big(self):
        source_file = pathlib.Path(cmi_tests, "test02")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if register > 16"

    def test_register_missing_prefix(self):
        source_file = pathlib.Path(cmi_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if register missing prefix"

    def test_hex_word_missing_prefix(self):
        source_file = pathlib.Path(cmi_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if hex word missing prefix"

    def test_hex_three_digits(self):
        source_file = pathlib.Path(cmi_tests, "test05")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if hex word only 12 bits"

    def test_hex_word_too_big(self):
        source_file = pathlib.Path(cmi_tests, "test06")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if hex word > 16 bits"

    def test_binary_word_too_big(self):
        source_file = pathlib.Path(cmi_tests, "test07")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if binary word > 16 bits"

    def test_decimal_too_negative(self):
        source_file = pathlib.Path(cmi_tests, "test08")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if decimal word < -32768"

    def test_decimal_too_large(self):
        source_file = pathlib.Path(cmi_tests, "test09")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if decimal word > 65536"

    def test_decimal_floats_not_allowed(self):
        source_file = pathlib.Path(cmi_tests, "test10")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "CMI assembly should fail if word is not an integer"

class TestJumpFailures:
    @pytest.mark.parametrize("src_file,assert_msg",
        [
            ("test01", "JE assembly should fail if address is missing prefix"),
            ("test02", "JE assembly should fail if address not 16 bits"),
            ("test03", "JE assembly should fail if destination is in the stack"),
            ("test04", "JG assembly should fail if address is missing prefix")
        ])
    def test_jump_failures(self, src_file, assert_msg):
        with open(pathlib.Path(jump_tests, src_file), "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg
