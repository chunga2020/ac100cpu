import pytest

import src.definitions as defs

class TestDefinitions:
    def test_architecture_sizes(self):
        assert defs.BYTE == 8, "BYTE should be 8: 8 bits in a byte"
        assert defs.BYTES_PER_WORD == 2, "Should have 2 bytes per machine word"
        assert defs.WORD_SIZE == 16, "Machine word should be 16 bits"

    def test_address_constants(self):
        assert defs.ADDRESS_MIN == 0, "Minimum address should be 0"
        assert defs.ADDRESS_SIZE == 65536,\
            "Address space should be 2^16 == 65536 bytes"
        assert defs.ADDRESS_MAX == 65535, "Address max should be 65535"
        assert defs.ADDRESS_SIZE - defs.ADDRESS_MAX == 1,\
            "Total address space and max address should differ by 1"
        assert defs.CODE_START == 0x0200, "Code section should start at 0x0200"

    def test_register_constants(self):
        assert defs.NUM_REGISTERS == 16, "Should have 16 gen-purpose registers"
        assert defs.REGISTER_MIN == 1, "Lowest usable register should be R1"
        assert defs.REGISTER_MAX == 16, "Highest register should be R16"
        assert defs.REGISTER_PREFIX == "R",\
            "Register name prefix should be 'R'"

    def test_stack_constants(self):
        assert defs.STACK_MIN == 0x200, "Stack should begin at 0x0200"
        assert defs.STACK_MAX == defs.ADDRESS_MIN,\
            "Stack should end at beginning of address space"

    def test_video_constants(self):
        assert defs.VIDEO_COLUMNS == 40,\
            f"Should have video width of 40 columns, but have"\
            f" {defs.VIDEO_COLUMNS} instead"
        assert defs.VIDEO_ROWS == 24,\
            f"Should have video height of 16 rows, but have"\
            f" {defs.VIDEO_ROWS} instead"
        # defaults give 256 bytes of VRAM -> 0xFFFF - 0x100 = FEFF
        assert defs.VRAM_START == 0xfc3f,\
            f"VRAM should start at 0xff00, but starts at "\
            f"{defs.VRAM_START}"

    def test_radix_prefixes(self):
        assert defs.BINARY_PREFIX == "0b" and len(defs.BINARY_PREFIX) == 2
        assert defs.HEX_PREFIX == "0x" and len(defs.HEX_PREFIX) == 2
