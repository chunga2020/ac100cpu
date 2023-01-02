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
