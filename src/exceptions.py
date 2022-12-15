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
