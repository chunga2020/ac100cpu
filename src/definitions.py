# Common definitions for the AC100

BYTE: int = 8                   # 8 bits in a byte
BYTES_PER_WORD: int = 2         # 16-bit architecture
WORD_SIZE: int = BYTE * BYTES_PER_WORD

ADDRESS_MIN: int = 0x0000
ADDRESS_SIZE: int = 2 ** WORD_SIZE # size of total address space
ADDRESS_MAX = ADDRESS_SIZE - 1

NUM_REGISTERS: int = 16
REGISTER_MIN: int = 1
REGISTER_MAX: int = 16

# stack pointer starts here on startup and grows towards low memory addresses
STACK_MIN: int = 0x0200
STACK_MAX: int = ADDRESS_MIN    # stack can’t go past here
