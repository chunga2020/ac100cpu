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


class TestDebuggingInfo:
    def test_dump_registers(self, capsys, emulator):
        expected = "R1: 0x0000\tR2: 0x0000\tR3: 0x0000\tR4: 0x0000\n"
        expected += "R5: 0x0000\tR6: 0x0000\tR7: 0x0000\tR8: 0x0000\n"
        expected += "R9: 0x0000\tR10: 0x0000\tR11: 0x0000\tR12: 0x0000\n"
        expected += "R13: 0x0000\tR14: 0x0000\tR15: 0x0000\tR16: 0x0000\n"
        emulator.dump_registers()
        capture = capsys.readouterr()
        assert capture.out == expected


def test_ldi_hex_values(assembler, capsys, emulator):
    # just make sure all registers are loaded
    slug = "ldi-test01"
    src_file = pathlib.Path(test_srcd, slug)
    bytecode = None
    with open(src_file, "r") as f:
        assembler.find_labels(f)
        bytecode = assembler.assemble(f)
        emulator.load_ram(bytecode)
    with pytest.raises(SystemExit):
        emulator.run()
    emulator.dump_registers()
    capture = capsys.readouterr()
    expected = "R1: 0x0011\tR2: 0x2233\tR3: 0x4455\tR4: 0x6677\n"
    expected += "R5: 0x8899\tR6: 0xaabb\tR7: 0xccdd\tR8: 0xeeff\n"
    expected += "R9: 0xffee\tR10: 0xddcc\tR11: 0xbbaa\tR12: 0x9988\n"
    expected += "R13: 0x7766\tR14: 0x5544\tR15: 0x3322\tR16: 0x1100\n"
    assert capture.out == expected


@pytest.mark.parametrize("bytecode, expected, msg",
    [
        (b"\x00\x00\x00\x00", True, "Should have set Z flag"),
        (b"\x00\x01\xbe\xef", False, "Should have cleared Z flag")
    ])
def test_ldi_z_flag(emulator, bytecode, expected, msg):
    emulator._exec_ldi(bytecode)
    z_set = emulator.flag_read(emu.AC100.FLAG_ZERO)
    assert z_set == expected, msg


@pytest.mark.parametrize("bytecode, expected, msg",
    [
        (b"\x00\x00\x88\x00", True, "Should have set N flag"),
        (b"\x00\x01\x00\x00", False, "Should have cleared N flag")
    ])
def test_ldi_n_flag(emulator, bytecode, expected, msg):
    emulator._exec_ldi(bytecode)
    n_set = emulator.flag_read(emu.AC100.FLAG_NEGATIVE)
    assert n_set == expected


def test_ldr(emulator):
    emulator._exec_ldi(b"\x00\x00\xde\xad") # LDI R1 0xdead
    assert (emulator.REGS[0][0] << 8 | emulator.REGS[0][1]) == 0xdead
    emulator._exec_ldr(b"\x01\x01\x00\x00") # LDR R2 R1
    assert (emulator.REGS[1][0] << 8 | emulator.REGS[1][1]) == 0xdead,\
        "LDR failed"


def test_ldr_z_flag_set(emulator):
    emulator._exec_ldi(b"\x00\x00\x00\x00") # LDI R1 0x0000; sets Z flag
    emulator._exec_ldi(b"\x00\x01\xbe\xef")  # LDI R2 0xbeef; clears Z flag
    emulator._exec_ldr(b"\x01\x01\x00\x00") # LDR R2 R1
    assert emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldr_z_flag_clear(emulator):
    emulator._exec_ldi(b"\x00\x00\xde\xad") # LDI R1 0xdead
    emulator._exec_ldi(b"\x00\x01\x00\x00") # LDR R2 0x0000; sets Z flag
    emulator._exec_ldr(b"\x01\x01\x00\x00") # LDR R2 R1; should clear Z flag
    assert not emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldr_n_flag_set(emulator):
    emulator._exec_ldi(b"\x00\x00\x80\x80") # LDI R1 0x8080; sets N flag
    emulator._exec_ldi(b"\x00\x01\x00\x00") # LDI R2 0x0000; clears N flag
    emulator._exec_ldr(b"\x01\x01\x00\x00") # LDR R2 R1; sets N flag
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_ldr_n_flag_clear(emulator):
    emulator._exec_ldi(b"\x00\x00\x00\x00") # LDI R1 0x0000; clears N flag
    emulator._exec_ldi(b"\x00\x01\x80\x80") # LDI R2 0x8080; sets N flag
    emulator._exec_ldr(b"\x01\x01\x00\x00") # LDR R2 R1; clears N flag
    assert not emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_ldm(emulator):
    emulator._exec_ldi(b"\x00\x00\xab\xcd") # LDI R1 0xabcd
    emulator._exec_st(b"\x10\x00\x05\x00")  # ST R1 0x0500
    assert emulator.RAM[0x0500] == 0xab
    assert emulator.RAM[0x0501] == 0xcd
    emulator._exec_ldm(b"\x02\x01\x05\x00") # LDM R2 0x0500
    assert emulator.REGS[1][0] == 0xab
    assert emulator.REGS[1][1] == 0xcd


def test_ldm_z_flag_set(emulator):
    emulator._exec_ldi(b"\x00\x01\x00\x00") # LDI R2 0x0000
    emulator._exec_ldi(b"\x00\x00\xde\xad") # LDI R1 0xdead
    assert not emulator.flag_read(emu.AC100.FLAG_ZERO)
    emulator._exec_st(b"\x10\x01\x04\x00") # ST R2 0x0400
    emulator._exec_ldm(b"\x02\x00\x04\x00") # LDM R1 0x0400
    assert emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldm_z_flag_clear(emulator):
    emulator._exec_ldi(b"\x00\x00\xde\xad") # LDI R1 0xdead
    emulator._exec_ldi(b"\x00\x01\x00\x00") # LDI R2 0x0000
    assert emulator.flag_read(emu.AC100.FLAG_ZERO)
    emulator._exec_st(b"\10\x00\x03\x00") # ST R1 0x0300
    emulator._exec_ldm(b"\x02\x01\x03\x00") # LDM R2 0x0300
    assert not emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldm_n_flag_set(emulator):
    emulator._exec_ldi(b"\x00\x00\xff\x00") # LDI R1 0x8000
    emulator._exec_ldi(b"\x00\x01\x00\x00") # LDI R2 0x0000
    assert not emulator.flag_read(emu.AC100.FLAG_NEGATIVE)
    emulator._exec_st(b"\x10\x00\x05\x00") # ST R1 0x0500
    emulator._exec_ldm(b"\x02\x01\x05\x00") # LDM R2 0x0500
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_ldm_n_flag_clear(emulator):
    emulator._exec_ldi(b"\x00\x00\x00\xff") # LDI R1 0xff
    emulator._exec_ldi(b"\x00\x01\xff\xee") # LDI R2 0xffee
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE)
    emulator._exec_st(b"\x10\x00\x05\x00") # ST R1 0x0500
    emulator._exec_ldm(b"\x02\x01\x05\x00") # LDM R2 0x0500
    assert not emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_st_valid_destination(emulator):
    emulator._exec_ldi(b"\x00\x00\xbe\xef") # LDI R1 0xbeef
    emulator._exec_st(b"\x10\x00\x04\x00") # ST R1 0x0400
    assert emulator.RAM[0x0400] == 0xbe and emulator.RAM[0x0401] == 0xef


def test_st_invalid_destination(emulator):
    emulator._exec_ldi(b"\x00\x00\xbe\xef") # LDI R1 0xbeef
    with pytest.raises(SystemExit):
        emulator._exec_st(b"\x10\x00\x01\x00") # ST R1 0x0100; stack space


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
