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
addi_tests = pathlib.Path(test_srcd, "addi_tests")

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
    @pytest.mark.parametrize("src_file, assert_msg",
        [
            ("test01", "LDM assembly should fail if dest register < 1"),
            ("test02", "LDM assembly should fail if dest register > 16"),
            ("test03", "LDM assembly should fail if dest register missing prefix"),
            ("test04", "LDM assembly should fail if src address given in decimal"),
            ("test05", "LDM assembly should fail if hex address < 16 bits wide")
        ])
    def test_ldm_failures(self, src_file, assert_msg):
        with open(pathlib.Path(ldm_tests, src_file), "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg


class TestStFailures:
    @pytest.mark.parametrize("src_file, assert_msg",
        [
            ("test01", "ST assembly should fail if src register < 1"),
            ("test02", "ST assembly should fail if src register > 16"),
            ("test03", "ST assembly should fail if src register missing prefix"),
            ("test04", "ST assembly should fail if address is missing hex prefix"),
            ("test05", "ST assembly should fail if hex address not 16 bits wide"),
            ("test06", "ST assembly should fail if hex address > 16 bits wide")
        ])
    def test_st_failures(self, src_file, assert_msg):
        source_file = pathlib.Path(st_tests, src_file)
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg


class TestCmrFailures:
    @pytest.mark.parametrize("src_file, assert_msg",
        [
            ("test01", "CMR assembly should fail if dest register missing prefix"),
            ("test02", "CMR assembly should fail if dest register < 1"),
            ("test03", "CMR assembly should fail if dest register > 16"),
            ("test04", "CMR assembly should fail if src register missing prefix"),
            ("test05", "CMR assembly should fail if src register < 1"),
            ("test06", "CMR assembly should fail if src register > 16")
        ])
    def test_cmr_failures(self, src_file, assert_msg):
        source_file = pathlib.Path(cmr_tests, src_file)
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg


class TestCmiFailures:
    @pytest.mark.parametrize("src_file, assert_msg",
        [
            ("test01", "CMI assembly should fail if register < 1"),
            ("test02", "CMI assembly should fail if register > 16"),
            ("test03", "CMI assembly should fail if register missing prefix"),
            ("test04", "CMI assembly should fail if hex word missing prefix"),
            ("test05", "CMI assembly should fail if hex word only 12 bits"),
            ("test06", "CMI assembly should fail if hex word > 16 bits"),
            ("test07", "CMI assembly should fail if binary word > 16 bits"),
            ("test08", "CMI assembly should fail if decimal word < -32768"),
            ("test09", "CMI assembly should fail if decimal word > 65536"),
            ("test10", "CMI assembly should fail if word is not an integer")
        ])
    def test_cmi_failures(self, src_file, assert_msg):
        source_file = pathlib.Path(cmi_tests, src_file)
        with open(source_file, "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg


class TestJumpFailures:
    @pytest.mark.parametrize("src_file,assert_msg",
        [
            ("test01", "JE assembly should fail if address is missing prefix"),
            ("test02", "JE assembly should fail if address not 16 bits"),
            ("test03", "JE assembly should fail if destination is in the stack"),
            ("test04", "JG assembly should fail if address is missing prefix"),
            ("test05", "JG assembly should fail if address not 16 bits"),
            ("test06", "JG assembly should fail if destination is in the stack"),
            ("test07", "JGE assembly should fail if address is missing prefix"),
            ("test08", "JGE assembly should fail if address not 16 bits"),
            ("test09", "JGE assembly should fail if destination is in the stack"),
            ("test10", "JL assembly should fail if address is missing prefix"),
            ("test11", "JL assembly should fail if address not 16 bits"),
            ("test12", "JL assembly should fail if destination is in the stack"),
            ("test13", "JLE assembly should fail if address is missing prefix"),
            ("test14", "JLE assembly should fail if address not 16 bits"),
            ("test15", "JLE assembly should fail if destination is in the stack"),
            ("test16", "JMP assembly should fail if address is missing prefix"),
            ("test17", "JMP assembly should fail if address not 16 bits"),
            ("test18", "JMP assembly should fail if destination is in the stack"),
            ("test19", "JE assembly should fail if dest not 4-byte aligned"),
            ("test20", "JG assembly should fail if dest not 4-byte aligned"),
            ("test21", "JGE assembly should fail if dest not 4-byte aligned"),
            ("test22", "JL assembly should fail if dest not 4-byte aligned"),
            ("test23", "JLE assembly should fail if dest not 4-byte aligned"),
            ("test24", "JMP assembly should fail if dest not 4-byte aligned")
        ])
    def test_jump_failures(self, src_file, assert_msg):
        with open(pathlib.Path(jump_tests, src_file), "r") as f:
            assembler.find_labels(f)
            print(assembler.labels)
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg


class TestAddiFailures:
    @pytest.mark.parametrize("src_file, assert_msg",
        [
            ("test01", "ADDI assembly should fail if register missing prefix"),
            ("test02", "ADDI assembly should fail if register < 0"),
            ("test03", "ADDI assembly should fail if register > 16"),
            ("test04", "ADDI assembly should fail if hex word missing prefix"),
            ("test05", "ADDI assembly should fail if hex word only three digits"),
            ("test06", "ADDI assembly should fail if hex word > 16 bits"),
            ("test07", "ADDI assembly should fail if decimal word < -32768"),
            ("test08", "ADDI assembly should fail if decimal word > 65535"),
            ("test09", "ADDI assembly should fail if decimal word is a float"),
            ("test10", "ADDI assembly should fail if binary word > 16 bits"),
            ("test11", "ADDI assembly should fail if binary word contains non-binary")
        ])
    def test_addi_failures(self, src_file, assert_msg):
        with open(pathlib.Path(addi_tests, src_file), "r") as f:
            bytecode = assembler.assemble(f)
            assert bytecode is None, assert_msg
