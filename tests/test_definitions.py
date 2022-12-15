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

    def test_register_constants(self):
        assert defs.NUM_REGISTERS == 16, "Should have 16 gen-purpose registers"
        assert defs.REGISTER_MIN == 1, "Lowest usable register should be R1"
        assert defs.REGISTER_MAX == 16, "Highest register should be R16"

    def test_stack_constants(self):
        assert defs.STACK_MIN == 0x200, "Stack should begin at 0x0200"
        assert defs.STACK_MAX == defs.ADDRESS_MIN,\
            "Stack should end at beginning of address space"
