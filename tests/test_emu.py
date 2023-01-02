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


    @pytest.mark.parametrize("flag",
        [
            emu.AC100.FLAG_CARRY, emu.AC100.FLAG_ZERO,
            emu.AC100.FLAG_OVERFLOW, emu.AC100.FLAG_NEGATIVE
        ])
    def test_flag_clear(self, emulator, flag):
        assert emulator.PS == 0
        ok = emulator.flag_set(flag)
        assert ok

        ok = emulator.flag_clear(flag)
        assert ok
        assert emulator.PS & flag == 0,\
            f"Flag {emulator.FLAG_NAMES[flag]} not cleared"

        # make sure flags remain cleared
        ok = emulator.flag_clear(flag)
        assert ok
        assert emulator.PS & flag == 0,\
            f"Flag {emulator.FLAG_NAMES[flag]} did not remain cleared"


    @pytest.mark.parametrize("flag",
        [
            emu.AC100.FLAG_CARRY, emu.AC100.FLAG_ZERO,
            emu.AC100.FLAG_OVERFLOW, emu.AC100.FLAG_NEGATIVE
        ])
    def test_flag_read(self, emulator, flag):
        assert emulator.PS == 0
        assert not emulator.flag_read(flag),\
            f"Flag {emulator.FLAG_NAMES[flag]} should be cleared on init"

        ok = emulator.flag_set(flag)
        assert ok
        assert emulator.flag_read(flag),\
            f"Flag {emulator.FLAG_NAMES[flag]} should be set"

        ok = emulator.flag_clear(flag)
        assert ok
        assert not emulator.flag_read(flag),\
            f"Flag {emulator.FLAG_NAMES[flag]} should be cleared"


    @pytest.mark.parametrize("flag, condition",
        [
            (emu.AC100.FLAG_CARRY, (0 == 0)),
            (emu.AC100.FLAG_CARRY, (0 == 1)),
            (emu.AC100.FLAG_ZERO, (0 == 0)),
            (emu.AC100.FLAG_ZERO, (0 == 1)),
            (emu.AC100.FLAG_OVERFLOW, (0 == 0)),
            (emu.AC100.FLAG_OVERFLOW, (0 == 1)),
            (emu.AC100.FLAG_NEGATIVE, (0 == 0)),
            (emu.AC100.FLAG_NEGATIVE, (0 == 1))
        ])
    def test_flag_set_or_clear(self, emulator, flag, condition):
        assert emulator.PS == 0
        emulator.flag_set_or_clear(flag, condition)
        if condition:
            assert emulator.flag_read(flag)
        else:
            assert not emulator.flag_read(flag)


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
