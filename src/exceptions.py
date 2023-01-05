# Exceptions for the AC100 emulator and assembler

import src.definitions as defs

class NegativeVideoDimensionError(Exception):
    def __init__(self, dimension):
        msg = f"Invalid {dimension} value: cannot be negative!"
        super().__init__(msg)


class VRAMTooLargeError(Exception):
    def __init__(self, dimension, value):
        msg = f"Invalid {dimension} value {value}: VRAM too large"
        super().__init__(msg)


class InvalidRegisterNameError(Exception):
    def __init__(self, name, min, max):
        msg = f"Invalid register name {name}. "\
            f"Valid names: R{defs.REGISTER_MIN}--R{defs.REGISTER_MAX}"
        super().__init__(msg)


class RegisterNameMissingPrefixError(Exception):
    def __init__(self, name):
        msg = f"Specified register {name} missing required prefix "\
            f"{defs.REGISTER_PREFIX}"
        super().__init__(msg)


class StackOverflowError(Exception):
    def __init__(self):
        super().__init__("Stack overflow")


class StackPointerAlignmentError(Exception):
    def __init__(self, address):
        self.address = address
        super().__init__(f"Stack pointer at 0x{self.address:04x} not 2-byte aligned")


class StackEmptyError(Exception):
    def __init__(self):
        super().__init__("Stack empty")


class StackJumpError(Exception):
    """ Exception raised if a program attempts to jump into stack space """
    def __init__(self, address):
        msg = "The program counter may not be set to addresses in stack space "
        msg = f"([0x{defs.STACK_MAX:04x}--0x{defs.STACK_MIN:04x}])"
        super().__init__(msg)


class VRAMJumpError(Exception):
    """ Exception raised if a program attempts to jump into VRAM """
    def __init__(self, address, vram_min, vram_max):
        msg = "The program counter may not be set to addresses in VRAM "
        msg += f"([0x{vram_min:04x}--0x{vram_max:04x}])"
        super().__init__(msg)


class PcAlignmentError(Exception):
    """ Exception raised if PC is not set to a four-byte aligned address """
    def __init__(self, address):
        msg = f"Program counter @ 0x{address:04x} not on four-byte boundary"
        super().__init__(msg)
