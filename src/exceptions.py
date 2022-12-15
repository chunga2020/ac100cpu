# Exceptions for the AC100 emulator and assembler

class NegativeVideoDimensionError(Exception):
    def __init__(self, dimension):
        msg = f"Invalid {dimension} value: cannot be negative!"
        super().__init__(msg)


class VRAMTooLargeError(Exception):
    def __init__(self, dimension, value):
        msg = f"Invalid {dimension} value {value}: VRAM too large"
        super().__init__(msg)
