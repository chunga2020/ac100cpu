# Common definitions for the AC100

BYTE: int = 8                   # 8 bits in a byte
BYTES_PER_WORD: int = 2         # 16-bit architecture
WORD_SIZE: int = BYTE * BYTES_PER_WORD

ADDRESS_MIN: int = 0x0000
ADDRESS_SIZE: int = 2 ** WORD_SIZE # size of total address space
ADDRESS_MAX = ADDRESS_SIZE - 1

REGISTER_PREFIX: str = "R"
NUM_REGISTERS: int = 16
REGISTER_MIN: int = 1
REGISTER_MAX: int = 16

# stack pointer starts here on startup and grows towards low memory addresses,
# giving us 512 bytes of stack space
STACK_MIN: int = 0x01FF
STACK_MAX: int = ADDRESS_MIN    # stack can’t go past here

# "video screen" is 16x16 by default
DEFAULT_VIDEO_COLUMNS: int = 16
DEFAULT_VIDEO_ROWS: int = 16
DEFAULT_VRAM_START: int = ADDRESS_MAX - \
    (DEFAULT_VIDEO_COLUMNS * DEFAULT_VIDEO_ROWS)

BINARY_PREFIX: str = "0b"
HEX_PREFIX: str = "0x"
