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


def test_ldi_hex_values(emulator):
    # just make sure all registers are loaded
    emulator._exec_load(b"\x00\x00\x00\x11")
    assert emulator.REGS[0] == [0x00, 0x11]

    emulator._exec_load(b"\x00\x01\x22\x33")
    assert emulator.REGS[1] == [0x22, 0x33]

    emulator._exec_load(b"\x00\x02\x44\x55")
    assert emulator.REGS[2] == [0x44, 0x55]

    emulator._exec_load(b"\x00\x03\x66\x77")
    assert emulator.REGS[3] == [0x66, 0x77]

    emulator._exec_load(b"\x00\x04\x88\x99")
    assert emulator.REGS[4] == [0x88, 0x99]

    emulator._exec_load(b"\x00\x05\xaa\xbb")
    assert emulator.REGS[5] == [0xaa, 0xbb]

    emulator._exec_load(b"\x00\x06\xcc\xdd")
    assert emulator.REGS[6] == [0xcc, 0xdd]

    emulator._exec_load(b"\x00\x07\xee\xff")
    assert emulator.REGS[7] == [0xee, 0xff]

    emulator._exec_load(b"\x00\x08\xff\xee")
    assert emulator.REGS[8] == [0xff, 0xee]

    emulator._exec_load(b"\x00\x09\xdd\xcc")
    assert emulator.REGS[9] == [0xdd, 0xcc]

    emulator._exec_load(b"\x00\x0a\xbb\xaa")
    assert emulator.REGS[10] == [0xbb, 0xaa]

    emulator._exec_load(b"\x00\x0b\x99\x88")
    assert emulator.REGS[11] == [0x99, 0x88]

    emulator._exec_load(b"\x00\x0c\x77\x66")
    assert emulator.REGS[12] == [0x77, 0x66]

    emulator._exec_load(b"\x00\x0d\x55\x44")
    assert emulator.REGS[13] == [0x55, 0x44]

    emulator._exec_load(b"\x00\x0e\x33\x22")
    assert emulator.REGS[14] == [0x33, 0x22]

    emulator._exec_load(b"\x00\x0f\x11\x00")
    assert emulator.REGS[15] == [0x11, 0x00]


@pytest.mark.parametrize("bytecode, expected, msg",
    [
        (b"\x00\x00\x00\x00", True, "Should have set Z flag"),
        (b"\x00\x01\xbe\xef", False, "Should have cleared Z flag")
    ])
def test_ldi_z_flag(emulator, bytecode, expected, msg):
    emulator._exec_load(bytecode)
    z_set = emulator.flag_read(emu.AC100.FLAG_ZERO)
    assert z_set == expected, msg


@pytest.mark.parametrize("bytecode, expected, msg",
    [
        (b"\x00\x00\x88\x00", True, "Should have set N flag"),
        (b"\x00\x01\x00\x00", False, "Should have cleared N flag")
    ])
def test_ldi_n_flag(emulator, bytecode, expected, msg):
    emulator._exec_load(bytecode)
    n_set = emulator.flag_read(emu.AC100.FLAG_NEGATIVE)
    assert n_set == expected


def test_ldr(emulator):
    emulator._exec_load(b"\x00\x00\xde\xad") # LDI R1 0xdead
    assert (emulator.REGS[0][0] << 8 | emulator.REGS[0][1]) == 0xdead
    emulator._exec_load(b"\x01\x01\x00\x00") # LDR R2 R1
    assert (emulator.REGS[1][0] << 8 | emulator.REGS[1][1]) == 0xdead,\
        "LDR failed"


def test_ldr_z_flag_set(emulator):
    emulator._exec_load(b"\x00\x00\x00\x00") # LDI R1 0x0000; sets Z flag
    emulator._exec_load(b"\x00\x01\xbe\xef")  # LDI R2 0xbeef; clears Z flag
    emulator._exec_load(b"\x01\x01\x00\x00") # LDR R2 R1
    assert emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldr_z_flag_clear(emulator):
    emulator._exec_load(b"\x00\x00\xde\xad") # LDI R1 0xdead
    emulator._exec_load(b"\x00\x01\x00\x00") # LDR R2 0x0000; sets Z flag
    emulator._exec_load(b"\x01\x01\x00\x00") # LDR R2 R1; should clear Z flag
    assert not emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldr_n_flag_set(emulator):
    emulator._exec_load(b"\x00\x00\x80\x80") # LDI R1 0x8080; sets N flag
    emulator._exec_load(b"\x00\x01\x00\x00") # LDI R2 0x0000; clears N flag
    emulator._exec_load(b"\x01\x01\x00\x00") # LDR R2 R1; sets N flag
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_ldr_n_flag_clear(emulator):
    emulator._exec_load(b"\x00\x00\x00\x00") # LDI R1 0x0000; clears N flag
    emulator._exec_load(b"\x00\x01\x80\x80") # LDI R2 0x8080; sets N flag
    emulator._exec_load(b"\x01\x01\x00\x00") # LDR R2 R1; clears N flag
    assert not emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_ldm(emulator):
    emulator._exec_load(b"\x00\x00\xab\xcd") # LDI R1 0xabcd
    emulator._exec_store(b"\x10\x00\x05\x00")  # ST R1 0x0500
    assert emulator.RAM[0x0500] == 0xab
    assert emulator.RAM[0x0501] == 0xcd
    emulator._exec_load(b"\x02\x01\x05\x00") # LDM R2 0x0500
    assert emulator.REGS[1][0] == 0xab
    assert emulator.REGS[1][1] == 0xcd


def test_ldm_indirect(emulator):
    emulator._exec_load(b"\x00\x00\x00\x2a") # LDI R1 42
    emulator._exec_load(b"\x00\x01\x05\x00") # LDI R2 0x0500
    emulator._exec_store(b"\x10\x00\x05\x00") # ST R1 0x0500
    assert emulator.RAM[0x0500] == 0x00
    assert emulator.RAM[0x0501] == 0x2a
    emulator._exec_load(b"\x02\x02\x00\x01")  # LDM R3 [R2]
    assert emulator.REGS[2][0] == 0x00
    assert emulator.REGS[2][1] == 0x2a


def test_ldm_z_flag_set(emulator):
    emulator._exec_load(b"\x00\x01\x00\x00") # LDI R2 0x0000
    emulator._exec_load(b"\x00\x00\xde\xad") # LDI R1 0xdead
    assert not emulator.flag_read(emu.AC100.FLAG_ZERO)
    emulator._exec_store(b"\x10\x01\x04\x00") # ST R2 0x0400
    emulator._exec_load(b"\x02\x00\x04\x00") # LDM R1 0x0400
    assert emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldm_z_flag_clear(emulator):
    emulator._exec_load(b"\x00\x00\xde\xad") # LDI R1 0xdead
    emulator._exec_load(b"\x00\x01\x00\x00") # LDI R2 0x0000
    assert emulator.flag_read(emu.AC100.FLAG_ZERO)
    emulator._exec_store(b"\x10\x00\x03\x00") # ST R1 0x0300
    emulator._exec_load(b"\x02\x01\x03\x00") # LDM R2 0x0300
    assert not emulator.flag_read(emu.AC100.FLAG_ZERO)


def test_ldm_n_flag_set(emulator):
    emulator._exec_load(b"\x00\x00\xff\x00") # LDI R1 0x8000
    emulator._exec_load(b"\x00\x01\x00\x00") # LDI R2 0x0000
    assert not emulator.flag_read(emu.AC100.FLAG_NEGATIVE)
    emulator._exec_store(b"\x10\x00\x05\x00") # ST R1 0x0500
    emulator._exec_load(b"\x02\x01\x05\x00") # LDM R2 0x0500
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_ldm_n_flag_clear(emulator):
    emulator._exec_load(b"\x00\x00\x00\xff") # LDI R1 0xff
    emulator._exec_load(b"\x00\x01\xff\xee") # LDI R2 0xffee
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE)
    emulator._exec_store(b"\x10\x00\x05\x00") # ST R1 0x0500
    emulator._exec_load(b"\x02\x01\x05\x00") # LDM R2 0x0500
    assert not emulator.flag_read(emu.AC100.FLAG_NEGATIVE)


def test_st_valid_destination(emulator):
    emulator._exec_load(b"\x00\x00\xbe\xef") # LDI R1 0xbeef
    emulator._exec_store(b"\x10\x00\x04\x00") # ST R1 0x0400
    assert emulator.RAM[0x0400] == 0xbe and emulator.RAM[0x0401] == 0xef


def test_st_invalid_destination(emulator):
    emulator._exec_load(b"\x00\x00\xbe\xef") # LDI R1 0xbeef
    with pytest.raises(SystemExit):
        emulator._exec_store(b"\x10\x00\x01\x00") # ST R1 0x0100; stack space


def test_sth(emulator):
    emulator._exec_load(b"\x00\x00\xbe\xef") # LDI R1 0xbeef
    emulator._exec_store(b"\x11\x00\x05\x00") # STH R1 0x0500
    assert emulator.RAM[0x0500] == 0xbe


def test_sth_invalid_destination(emulator):
    emulator._exec_load(b"\x00\x00\xde\xad") # LDI R1 0xdead
    with pytest.raises(SystemExit):
        emulator._exec_store(b"\x11\x00\x01\x00") # STH R1 0x0100; stack space


def test_stl(emulator):
    emulator._exec_load(b"\x00\x00\xab\xcd") # LDI R1 0xabcd
    emulator._exec_store(b"\x12\x00\x05\x00") # STL R1 0x0500
    assert emulator.RAM[0x0500] == 0xcd


def test_stl_invalid_destination(emulator):
    emulator._exec_load(b"\x00\x00\x7f\xff") # LDI R1 0x7fff
    with pytest.raises(SystemExit):
        emulator._exec_store(b"\x12\x00\x01\x00") # STL R1 0x0100; stack space


@pytest.mark.parametrize("a, b, carryin, expected",
    [
        (0, 0, 0, (0, 0)),
        (0, 1, 0, (0, 1)),
        (1, 0, 0, (0, 1)),
        (1, 1, 0, (1, 0)),
        (0, 0, 1, (0, 1)),
        (0, 1, 1, (1, 0)),
        (1, 0, 1, (1, 0)),
        (1, 1, 1, (1, 1))
    ])
def test_add_bits(emulator, a, b, carryin, expected):
    result = emulator._add_bits(a, b, carryin)
    assert result == expected


@pytest.mark.parametrize("a, b, expected",
    [
        (0, 0, (False, 0, False)),
        (0, 1, (False, 1 , False)),
        (1, 0, (False, 1, False)),
        (1, 1, (False, 2, False)),
        (5, 5, (False, 10, False)),
        (0xffff, 1, (True, 0, False)),
        (0x8000, 0x8000, (True, 0, True)),
        (0x7fff, 0x7fff, (False, 0xfffe, True))
    ])
def test_ripple_add(emulator, a, b, expected):
    result = emulator._ripple_add(a, b)
    assert result == expected


@pytest.mark.parametrize("a, b, c_set, n_set, z_set",
    [
        (0x5, 0x3, True, False, False),
        (0x3, 0x5, False, True, False),
        (0x3, 0x3, True, False, True),
        (0x5, 0xfffd, False, False, False),
        (0xfffd, 0x5, True, True, False)
    ])
def test_cmr(emulator, a, b, c_set, n_set, z_set):
    emulator._exec_load(b"\x00\x00" + a.to_bytes(2, byteorder='big')) # LDI R1 with a
    emulator._exec_load(b"\x00\x01" + b.to_bytes(2, byteorder='big')) # LDI R2 with b
    emulator._exec_cmp(b"\x20\x00\x01\x00")    # CMR R1 R2 (a - b)
    assert emulator.flag_read(emu.AC100.FLAG_CARRY) == c_set
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("a, b, c_set, n_set, z_set",
    [
        (0x5, 0x3, True, False, False),
        (0x3, 0x5, False, True, False),
        (0x3, 0x3, True, False, True),
        (0x5, 0xfffd, False, False, False),
        (0xfffd, 0x5, True, True, False)
    ])
def test_cmi(emulator, a, b, c_set, n_set, z_set):
    emulator._exec_load(b"\x00\x00" + a.to_bytes(2, byteorder='big'))
    emulator._exec_cmp(b"\x21\x00" + b.to_bytes(2, byteorder='big'))
    assert emulator.flag_read(emu.AC100.FLAG_CARRY) == c_set
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("flag, flag_set, opcode, before, after",
    [
        (emu.AC100.FLAG_ZERO, False, "JZ", 0x0200, 0x0700),
        (emu.AC100.FLAG_ZERO, False, "JZ", 0x703c, 0x3000),
        (emu.AC100.FLAG_ZERO, True, "JZ", 0x0200, 0x0400),
        (emu.AC100.FLAG_ZERO, True, "JZ", 0x703c, 0x0200),

        (emu.AC100.FLAG_ZERO, False, "JNZ", 0x0200, 0x0700),
        (emu.AC100.FLAG_ZERO, False, "JNZ", 0xab00, 0x0200),
        (emu.AC100.FLAG_ZERO, True, "JNZ", 0x0200, 0x0500),
        (emu.AC100.FLAG_ZERO, True, "JNZ", 0xab00, 0xa00c),

        (emu.AC100.FLAG_CARRY, False, "JC", 0x0200, 0x02a0),
        (emu.AC100.FLAG_CARRY, False, "JC", 0xab34, 0xab50),
        (emu.AC100.FLAG_CARRY, True, "JC", 0x0200, 0x0500),
        (emu.AC100.FLAG_CARRY, True, "JC", 0xab30, 0x0200),

        (emu.AC100.FLAG_CARRY, False, "JNC", 0x0200, 0x0254),
        (emu.AC100.FLAG_CARRY, False, "JNC", 0xcd00, 0x0300),
        (emu.AC100.FLAG_CARRY, True, "JNC", 0x0200, 0x0300),
        (emu.AC100.FLAG_CARRY, True, "JNC", 0xcd00, 0xca00),

        (emu.AC100.FLAG_NEGATIVE, False, "JN", 0x0200, 0x0700),
        (emu.AC100.FLAG_NEGATIVE, False, "JN", 0xcde0, 0xdea0),
        (emu.AC100.FLAG_NEGATIVE, True, "JN", 0x0200, 0x0500),
        (emu.AC100.FLAG_NEGATIVE, True, "JN", 0xabc0, 0x0200),

        (emu.AC100.FLAG_NEGATIVE, False, "JP", 0x0200, 0x0400),
        (emu.AC100.FLAG_NEGATIVE, False, "JP", 0xba00, 0x0300),
        (emu.AC100.FLAG_NEGATIVE, True, "JP", 0x0200, 0x05790),
        (emu.AC100.FLAG_NEGATIVE, True, "JP", 0xba08, 0xbd84),

        (emu.AC100.FLAG_OVERFLOW, False, "JV", 0x0200, 0x03840),
        (emu.AC100.FLAG_OVERFLOW, False, "JV", 0xbca0, 0xbf94),
        (emu.AC100.FLAG_OVERFLOW, True, "JV", 0x200, 0x0500),
        (emu.AC100.FLAG_OVERFLOW, True, "JV", 0xbca0, 0x0200),

        (emu.AC100.FLAG_OVERFLOW, False, "JNV", 0x0200, 0x4000),
        (emu.AC100.FLAG_OVERFLOW, False, "JNV", 0xde00, 0x0500),
        (emu.AC100.FLAG_OVERFLOW, True, "JNV", 0x0200, 0x2038),
        (emu.AC100.FLAG_OVERFLOW, True, "JNV", 0xde00, 0xdb94)
    ])
def test_conditional_jump(emulator, flag, flag_set, opcode, before, after):
    emulator.PC = before
    emulator.flag_set_or_clear(flag, flag_set)
    jump_code = b""
    expect_jump = False
    match opcode:
        case "JZ":
            jump_code = b"\x30"
            expect_jump = flag_set
        case "JNZ":
            jump_code = b"\x31"
            expect_jump = not flag_set
        case "JC":
            jump_code = b"\x32"
            expect_jump = flag_set
        case "JNC":
            jump_code = b"\x33"
            expect_jump = not flag_set
        case "JN":
            jump_code = b"\x34"
            expect_jump = flag_set
        case "JP":
            jump_code = b"\x35"
            expect_jump = not flag_set
        case "JV":
            jump_code = b"\x36"
            expect_jump = flag_set
        case "JNV":
            jump_code = b"\x37"
            expect_jump = not flag_set
    jump_code += b"\x00" + after.to_bytes(2, byteorder='big')
    emulator._exec_jump(jump_code)
    if expect_jump:
        assert emulator.PC == after
    else:
        assert emulator.PC == before + 4


@pytest.mark.parametrize("before, after",
    [
        (0x0200, 0xabc0), (0x0200, 0x0200), (0xabc0, 0x0200)
    ])
def test_unconditional_jump(emulator, before, after):
    emulator.PC = before
    code = b"\x38\x00" + after.to_bytes(2, byteorder='big')
    emulator._exec_jump(code)
    assert emulator.PC == after


@pytest.mark.parametrize("before, after, opcode",
    [
        (0x0200, 0x0100, b"\x30"), (0xab40, 0x0040, b"\x30"),
        (0x0200, 0x01fc, b"\x30"), (0x0300, 0x0000, b"\x30")
    ])
def test_jump_stack_jump_error(emulator, before, after, opcode):
    emulator.PC = before
    emulator.flag_set(emu.AC100.FLAG_ZERO)
    address_code = after.to_bytes(2, byteorder='big')
    jump_code = opcode + b"\x00" + address_code
    with pytest.raises(ac_exc.StackJumpError):
        emulator._exec_jump(jump_code)


@pytest.mark.parametrize("before, after, opcode",
    [
        (0x0200, defs.VRAM_START, b"\x30"),
        (0x0440, defs.ADDRESS_MAX, b"\x30"),
        (0xabc0, defs.ADDRESS_MAX - 10, b"\x30")
    ])
def test_jump_vram_jump_error(emulator, before, after, opcode):
    emulator.PC = before
    emulator.flag_set(emu.AC100.FLAG_ZERO)
    address_code = after.to_bytes(2, byteorder='big')
    jump_code = opcode + b"\x00" + address_code
    with pytest.raises(ac_exc.VRAMJumpError):
        emulator._exec_jump(jump_code)


@pytest.mark.parametrize("before, after, opcode",
    [
        (0x0200, 0xbeef, b"\x30"), (0x0200, 0x0301, b"\x30")
    ])
def test_jump_pc_alignment_error(emulator, before, after, opcode):
    emulator.PC = before
    emulator.flag_set(emu.AC100.FLAG_ZERO)
    address_code = after.to_bytes(2, byteorder='big')
    jump_code = opcode + b"\x00" + address_code
    with pytest.raises(ac_exc.PcAlignmentError):
        emulator._exec_jump(jump_code)


@pytest.mark.parametrize("a, b, sum, c_set, n_set, v_set, z_set",
    [
        (0x0001, 0x0001, 0x0002, False, False, False, False),
        (0x7fff, 0x0001, 0x8000, False, True, True, False),
        (0x8000, 0x8000, 0x0000, True, False, True, True),
        (0xffff, 0x0001, 0x0000, True, False, False, True),
        (0xffff, 0xffff, 0xfffe, True, True, False, False)
    ])
def test_addi(emulator, a, b, sum, c_set, n_set, v_set, z_set):
    emulator._exec_load(b"\x00\x00" + a.to_bytes(2, byteorder='big'))
    emulator._exec_add_sub(b"\x40\x00" + b.to_bytes(2, byteorder='big'))
    calc_sum = emulator.REGS[0][0] << 8 | emulator.REGS[0][1]
    assert calc_sum == sum
    assert emulator.flag_read(emu.AC100.FLAG_CARRY) == c_set
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_OVERFLOW) == v_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("a, b, sum, c_set, n_set, v_set, z_set",
    [
        (0x0001, 0x0001, 0x0002, False, False, False, False),
        (0x7fff, 0x0001, 0x8000, False, True, True, False),
        (0x8000, 0x8000, 0x0000, True, False, True, True),
        (0xffff, 0x0001, 0x0000, True, False, False, True),
        (0xffff, 0xffff, 0xfffe, True, True, False, False)
    ])
def test_addr(emulator, a, b, sum, c_set, n_set, v_set, z_set):
    emulator._exec_load(b"\x00\x00" + a.to_bytes(2, byteorder='big'))
    emulator._exec_load(b"\x00\x01" + b.to_bytes(2, byteorder='big'))
    emulator._exec_add_sub(b"\x41\x00\x01\x00")
    calc_sum = emulator.REGS[0][0] << 8 | emulator.REGS[0][1]
    assert calc_sum == sum
    assert emulator.flag_read(emu.AC100.FLAG_CARRY) == c_set
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_OVERFLOW) == v_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("a, b, diff, c_set, n_set, v_set, z_set",
    [
        (0x0001, 0x0001, 0x0000, True, False, False, True),
        (0x0000, 0x0001, 0xffff, False, True, False, False),
        (0xffff, 0xffff, 0x0000, True, False, False, True),
        (0xffff, 0x0001, 0xfffe, True, True, False, False),
        (0xfffe, 0xffff, 0xffff, False, True, False, False)
    ])
def test_subi(emulator, a, b, diff, c_set, n_set, v_set, z_set):
    emulator._exec_load(b"\x00\x00" + a.to_bytes(2, byteorder='big'))
    emulator._exec_add_sub(b"\x43\x00" + b.to_bytes(2, byteorder='big'))
    calc_diff = emulator.REGS[0][0] << 8 | emulator.REGS[0][1]
    assert calc_diff == diff
    assert emulator.flag_read(emu.AC100.FLAG_CARRY) == c_set
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_OVERFLOW) == v_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("a, b, diff, c_set, n_set, v_set, z_set",
    [
        (0x0001, 0x0001, 0x0000, True, False, False, True),
        (0x0000, 0x0001, 0xffff, False, True, False, False),
        (0xffff, 0xffff, 0x0000, True, False, False, True),
        (0xffff, 0x0001, 0xfffe, True, True, False, False),
        (0xfffe, 0xffff, 0xffff, False, True, False, False)
    ])
def test_subr(emulator, a, b, diff, c_set, n_set, v_set, z_set):
    emulator._exec_load(b"\x00\x00" + a.to_bytes(2, byteorder='big'))
    emulator._exec_load(b"\x00\x01" + b.to_bytes(2, byteorder='big'))
    emulator._exec_add_sub(b"\x44\x00\x01\x00")
    calc_diff = emulator.REGS[0][0] << 8 | emulator.REGS[0][1]
    assert calc_diff == diff
    assert emulator.flag_read(emu.AC100.FLAG_CARRY) == c_set
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_OVERFLOW) == v_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("value_before,value_after,n_set,z_set",
    [
        (0, 1, False, False),
        (0x1234, 0x1235, False, False),
        (0x7fff, 0x8000, True, False),
        (0x8000, 0x8001, True, False),
        (0xffff, 0, False, True)
    ])
def test_inc(emulator, value_before, value_after, n_set, z_set):
    load_value = value_before.to_bytes(2, byteorder='big')
    load_code = b"\x00\x00" + load_value
    emulator._exec_load(load_code)
    emulator._exec_inc(b"\x42\x00\x00\x00")
    actual_value = (emulator.REGS[0][0] << 8 | emulator.REGS[0][1]) & 0xffff
    assert actual_value == value_after
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


@pytest.mark.parametrize("value_before, value_after, n_set, z_set",
    [
        (1, 0, False, True),
        (0, 0xffff, True, False),
        (0x1234, 0x1233, False, False),
        (0x8001, 0x8000, True, False)
    ])
def test_dec(emulator, value_before, value_after, n_set, z_set):
    load_value = value_before.to_bytes(2, byteorder='big')
    load_code = b"\x00\x00" + load_value
    emulator._exec_load(load_code)
    emulator._exec_dec(b"\x45\x00\x00\x00")
    actual_value = (emulator.REGS[0][0] << 8 | emulator.REGS[0][1]) & 0xffff
    assert actual_value == value_after
    assert emulator.flag_read(emu.AC100.FLAG_NEGATIVE) == n_set
    assert emulator.flag_read(emu.AC100.FLAG_ZERO) == z_set


def test_push(emulator):
    emulator._exec_load(b"\x00\x00\xab\xcd")
    assert emulator.SP == defs.STACK_MIN
    emulator._exec_push(b"\xe0\x00\x00\x00")
    assert emulator.SP == defs.STACK_MIN - 2
    assert emulator.RAM[defs.STACK_MIN - 2] == 0xab
    assert emulator.RAM[defs.STACK_MIN - 1] == 0xcd

    emulator._exec_load(b"\x00\x01\xde\xad")
    emulator._exec_push(b"\xe0\x01\x00\x00")
    assert emulator.SP == defs.STACK_MIN - 4
    assert emulator.RAM[defs.STACK_MIN - 4] == 0xde
    assert emulator.RAM[defs.STACK_MIN - 3] == 0xad
    assert emulator.RAM[defs.STACK_MIN - 2] == 0xab
    assert emulator.RAM[defs.STACK_MIN - 1] == 0xcd


def test_push_alignment_check(emulator):
    emulator._exec_load(b"\x00\x00\xab\xcd")
    emulator.SP = 0x01FD
    with pytest.raises(ac_exc.StackPointerAlignmentError):
        emulator._exec_push(b"\xe0\x00\x00\x00")


def test_push_overflow(emulator):
    emulator._exec_load(b"\x00\x00\xde\xad")
    emulator.SP = defs.ADDRESS_MIN
    with pytest.raises(ac_exc.StackOverflowError):
        emulator._exec_push(b"\xe0\x00\x00\x00")


def test_pop(emulator):
    emulator._exec_load(b"\x00\x00\x12\x34")
    emulator._exec_push(b"\xe0\x00\x00\x00")
    assert emulator.RAM[emulator.SP] == 0x12
    assert emulator.RAM[emulator.SP + 1] == 0x34

    emulator._exec_pop(b"\xe1\x01\x00\x00")
    assert emulator.SP == defs.STACK_MIN
    assert emulator.REGS[1][0] == 0x12
    assert emulator.REGS[1][1] == 0x34


def test_pop_empty_stack(emulator):
    assert emulator.SP == defs.STACK_MIN
    with pytest.raises(ac_exc.StackEmptyError):
        emulator._exec_pop(b"\xe1\x00\x00\x00")


def test_pop_alignment_check(emulator):
    emulator._exec_load(b"\x00\x00\xde\xad")
    emulator._exec_push(b"\xe0\x00\x00\x00")
    assert emulator.SP == defs.STACK_MIN - 2
    emulator.SP -= 1
    with pytest.raises(ac_exc.StackPointerAlignmentError):
        emulator._exec_pop(b"\xe1\x01\x00\x00")
 
