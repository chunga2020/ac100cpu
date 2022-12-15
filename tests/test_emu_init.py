import pytest

import src.definitions as defs
import src.ac100 as ac100

class TestEmulatorInit:
    def test_register_init(self):
        machine = ac100.AC100()
        assert len(machine.REGS) == defs.NUM_REGISTERS,\
            f"Should have {defs.NUM_REGISTERS} registers, have {len(machine.REGS)}"
        assert sum(len(reg) for reg in machine.REGS) == 32,\
            "Machine registers should occupy total of 32 bytes"
        for i in range(len(machine.REGS)):
            assert len(machine.REGS[i]) == defs.BYTES_PER_WORD,\
                f"Register {i} is the wrong size!"

    def test_ram_init(self):
        machine = ac100.AC100()
        assert len(machine.RAM) == defs.ADDRESS_SIZE,\
            f"RAM should be {defs.ADDRESS_SIZE} bytes, is {len(machine.RAM)}"
        for i in range(len(machine.RAM)):
            assert machine.RAM[i] == 0x0,\
                f"RAM byte {i} not zeroed on initialization"

    def test_status_init(self):
        machine = ac100.AC100()
        assert machine.PS == 0x00,\
            f"Machine status register should be 0 on init, but is {machine.PS}"

    def test_stack_pointer_init(self):
        machine = ac100.AC100()
        assert machine.SP == defs.STACK_MIN,\
            f"Stack pointer incorrectly set to {machine.SP} on init, "\
            f"should be {defs.STACK_MIN}"
