import pathlib
import pytest

import src.definitions as defs
import src.exceptions as ac_exc
import src.ac100asm as asm
import src.ac100 as emu

@pytest.fixture
def assembler():
    return asm.AC100ASM()

@pytest.fixture
def emulator():
    return emu.AC100()

test_srcd = pathlib.Path("emu_tests")

class TestFlags:
    @pytest.mark.parametrize("flag",
        [
            emu.AC100.FLAG_CARRY, emu.AC100.FLAG_ZERO,
            emu.AC100.FLAG_OVERFLOW, emu.AC100.FLAG_NEGATIVE
        ])
    def test_flag_set(self, emulator, flag):
        assert emulator.PS == 0
        ok = emulator.flag_set(flag)
        assert ok
        assert emulator.PS & flag == flag,\
            f"Flag {emulator.FLAG_NAMES[flag]} not set"

        # make sure flags remain set
        ok = emulator.flag_set(flag)
        assert ok
        assert emulator.PS & flag == flag,\
            f"Flag {emulator.FLAG_NAMES[flag]} did not remain set"


def test_halt(assembler, emulator):
    slug = "halt-test01"
    src_file = pathlib.Path(test_srcd, slug)
    bytecode = None
    with open(src_file, "r") as f:
        assembler.find_labels(f)
        bytecode = assembler.assemble(f)
    emulator.load_ram(bytecode)
    with pytest.raises(SystemExit):
        emulator.run()

def test_nop(assembler, emulator):
    slug = "nop-test01"
    src_file = pathlib.Path(test_srcd, slug)
    bytecode = None
    with open(src_file, "r") as f:
        assembler.find_labels(f)
        bytecode = assembler.assemble(f)
    emulator.load_ram(bytecode)
    with pytest.raises(SystemExit):
        emulator.run()
