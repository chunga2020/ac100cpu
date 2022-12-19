import pathlib

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
    def test_je_fails_address_no_prefix(self):
        source_file = pathlib.Path(jump_tests, "test01")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "JE assembly should fail if address is missing prefix"

    def test_je_fails_address_not_16_bits(self):
        source_file = pathlib.Path(jump_tests, "test02")
        with open(source_file,"r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "JE assembly should fail if address not 16 bits"

    def test_je_fails_jumping_to_stack(self):
        source_file = pathlib.Path(jump_tests, "test03")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "JE assembly should fail if destination is in the stack"

    def test_jg_fails_address_no_prefix(self):
        source_file = pathlib.Path(jump_tests, "test04")
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None,\
                "JG assembly should fail if address is missing prefix"
