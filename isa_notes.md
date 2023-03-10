# AC100 Instruction Set Architecture

-   16-bit big-endian architecture
-   32-bit instructions (16-bit opcode, 16-bit data); this means that every
    instruction is 4 bytes for easy alignment
-   No direct ops on memory
-   16 general-purpose registers R1-R16



## Terminology conventions

-   **Byte:** 8-bit data object
-   **Word:** 16-bit data object



## Instruction bytecode format

-   byte 0: opcode
-   byte 1: register on which to operate
-   bytes 2, 3: data/address
-   Any unused bytes should be set to 0x00



## Source file format

-   Comments started by ; and extend to end-of-line
    -   Multiline comments are therefore just a block of comment lines
-   Comments may **NOT** occur on the same line as any code or label
-   Labels
    -   Format: label\_name ":" new\_line
    -   Valid characters: [`a-zA-Z0-9\_`] (corresponds to Python re's '`\w`' sequence)
-   Numerical base prefixes
    -   **Decimal:** no prefix (default)
        -   Ranges:
            -   Unsigned: 0--65535
            -   Signed: (-32768--+32767)
    -   **Binary:** '0b' -> '0bnnnnnnnn' represents a byte in binary
    -   **Hexadecimal:** '0x' -> '0xhh' represents a byte in hex
        -   Hex values may be given as one byte (0xhh) or two (0xhhhh)
-   Register names must be prefixed with 'R'
    -   e.g. R1 means register 1
    -   All registers are assumed to be given in decimal, *i.e.* tenth register
        (decimal) is R10, **not** RA; eleventh register is R11, not RB, *etc.*



## Data structures

-   Flags register PS
    -   8 bits: ---- NVZC
        -   **N:** Negative
            -   1 if most-significant bit of destination register set by operation
            -   0 if most-significant bit of destination register cleared by operation
        -   **V:** oVerflow
            -   **Signed** overflow occurred
                -   If we have A + B = C, V is set when:
                    -   A < 0, B < 0, C > 0
                        -   MSB of A set
                        -   MSB of B set
                        -   MSB of C cleared
                    -   A > 0, B > 0, C < 0
                        -   MSB of A cleared
                        -   MSB of B cleared
                        -   MSB of C set
                -   If we have A - B = C, V is set when:
                    -   A > 0, B < 0, C < 0
                        -   MSB of A cleared
                        -   MSB of B set
                        -   MSB of C set
                    -   A < 0, B > 0, C > 0
                        -   MSB of A set
                        -   MSB of B cleared
                        -   MSB of C cleared
                -   And cleared otherwise
        -   **Z:** Zero
            -   1 if last operation set destination register to zero
            -   0 if last operation set destination register to non-zero
        -   **C:** Carry
            -   **Unsigned** overflow occurred
                -   ~C before operation: result is less than initial values
                -   C before operation: result
            -   Comparisons: destination register (first operand of pseudo-subtraction)
                greater than source (second operand of pseudo-subtraction)
-   Stack Pointer SP
    -   Stack: memory 0x0000--0x0200
    -   Begins at 0x0200 and grows towards 0x0000
    -   The contents of any GPR R1--R16 may be pushed onto the stack; stack values
        may likewise be popped off and stored in any of the GPRs
    -   Stack overflow exceptions cause immediate halt of emulator and dump of the
        machine state: registers, memory, flags



## Opcodes



### LOAD

-   **0x00:** Load immediate word into register (LDI)
    -   Syntax: 0x00 <dest\_reg> <word high byte> <word low byte>
    -   Example: LDI R1 4
        -   Load immediate 0x0004 into R1
-   **0x01:** Load word from register into register (LDR)
    -   Syntax: 0x01 <dest\_reg> <src\_reg> <unused>
    -   Example: LDR R1 R2
        -   Load the contents of R2 into R1
-   **0x02:** Load word from memory into register (LDM)
    -   Syntax: 0x02 <dest\_reg> <addr high byte> <addr low byte>
    -   Example: LDM R1 0xbeef
        -   Load the word beginning at memory address 0xbeef into R1
    -   Example: LDM R1 [R2]
        -   Load into R1 the word beginning at the address stored in R2
        -   Address is given as the register number, for the machine to compute at
            runtime
-   **0x03:** Load byte from memory into register (LDBM)
    -   Syntax: 0x03 <dest\_reg> <addr high byte> <addr low byte>
    -   Example: LDBM R1 0x0500
        -   Load the byte at 0x0500 into R1
    -   Example: LDBM R1 [R2]
        -   Load into R1 the byte at the address stored in R2



### STORE

-   **0x10:** Store word from register into memory (ST)
    -   Syntax: 0x10 <src\_reg> <addr high byte> <addr low byte>
    -   Example: ST R1 0xabcd
        -   Store the word in R1 at memory location 0xabcd
-   **0x11:** Store high byte from register into memory (STH)
    -   Syntax: 0x11 <src\_reg> <addr high byte> <addr low byte>
    -   Example: STH R3 0x1234
        -   Store the high byte of R3 at memory location 0x1234
-   **0x12:** Store low byte from register into memory (STL)
    -   Syntax: 0x12 <src\_reg> <addr high byte> <addr low byte>
    -   Example: STL R4 0x5678
        -   Store the low byte of R4 at memory location 0x5678



### COMPARE

-   **0x20:** Compare register with register (CMR)
    -   Syntax: 0x20 <dest\_reg> <src\_reg> <unused>
    -   Example: CMR R1 R2
        -   Compare the contents of R1 with the contents of R2
-   **0x21:** Compare register with immediate word (CMI)
    -   Syntax: 0x21 <reg> <word high byte> <word low byte>
    -   Example: CMI R1 5
        -   Compare the contents of R1 to 0x05



### JUMP

-   All jump instructions may take a raw address or a label (see JZ examples)
-   **0x30:** Jump if zero (JZ)
    -   Syntax: 0x30 <unused> <addr high byte> <addr low byte>
    -   Example 1: JZ 0x1234
        -   If the zero bit is 1, jump to memory location 0x1234 and continue
            execution
    -   Example 2: JZ done
        -   Assuming 'done' is a valid previously-defined label, if the zero bit is 1,
            jump to the memory location associated with the label 'done'
-   **0x31:** Jump if not zero (JNZ)
    -   Syntax: 0x31 <unused> <addr high byte> <addr low byte>
    -   Example: JNZ 0x2400
        -   If the zero bit is 0, jump to memory location 0x2400 and continue
            execution
-   **0x32:** Jump if carry (JC)
    -   Syntax: 0x32 <unused> <addr high byte> <addr low byte>
    -   Example 1: JC 0x2255
        -   If the carry bit is 1, jump to memory location 0x2255 and continue
            execution
-   **0x33:** Jump if no carry (JNC)
    -   Syntax: 0x33 <unused> <addr high byte> <addr low byte>
    -   Example: JNC 0x57ab
        -   If the carry bit is 0, jump to memory location 0x57ab and continue
            execution
-   **0x34:** Jump if negative (JN)
    -   Syntax: 0x34 <unused> <addr high byte> <addr low byte>
    -   Example: JN 0x7890
        -   If the sign bit is 1, jump to memory location 0x7890 and continue
            execution
-   **0x35:** Jump if positive (JP)
    -   Syntax: 0x35 <unused> <addr high byte> <addr low byte>
    -   Example: JP 0x02ab
        -   If the sign bit is 0, jump to memory location 0x02ab and continue
            execution
-   **0x36:** Jump if overflow (JV)
    -   Syntax: 0x36 <unused> <addr high byte> <addr low byte>
    -   Example: JV 0x1234
        -   If the overflow bit is 1, jump to memory location 0x1234 and continue
            execution
-   **0x37:** Jump if no overflow (JNV)
    -   Syntax: 0x37 <unused> <addr high byte> <addr low byte>
    -   Example: JNV 0x0x0300
        -   If the overflow bit is 0, jump to memory location 0x0300 and continue
            execution
-   **0x38:** Jump always (JMP)
    -   Syntax: 0x38 <unused> <addr high byte> <addr low byte>
    -   Example: JMP 0x1234
        -   Unconditionally jump to memory location 0x1234 and continue execution
-   **0x39:** Jump to Subroutine (JSR)
    -   Syntax: 0x39 <unused> <addr high byte> <addr low byte>
    -   Example: JSR putchar
        -   Save to the stack the address of the instruction after the JSR, then jump
            to the subroutine named ???putchar???



### MATH

-   **0x40:** Add immediate word to register (ADDI)
    -   Syntax: 0x40 <dest\_reg> <word high byte> <word low byte>
    -   Example: ADDI R1 0x0a
        -   Add 0xa to the contents of R1
-   **0x41:** Add register word to register (ADDR)
    -   Syntax: 0x41 <dest\_reg> <src\_reg> <unused>
    -   Example: ADDR R1 R2
        -   Add the contents of R2 to the contents of R1 and store in R1
-   **0x42:** Increment (INC)
    -   Syntax: 0x42 <register> <unused> <unused>
    -   Example: INC R3
        -   Increment (add one) to the value in R3
-   **0x43:** Subtract immediate word from register (SUBI)
    -   Syntax: 0x43 <register> <word high byte> <word low byte>
    -   Example: SUBI R3 5
        -   Subtract 0x5 from the value in R3
-   **0x44:** Subtract register word from register (SUBR)
    -   Syntax: 0x44 <dest\_reg> <src\_reg> <unused>
    -   Example: SUBR R3 R7
        -   Subtract the contents of R7 from the contents of R3 and store in R3
-   **0x45:** Decrement (DEC)
    -   Syntax: 0x45 <register> <unused> <unused>
    -   Example: DEC R8
        -   Decrement (subtract one from) the value in R8



### STACK MANIPULATION

-   **0xE0:** Push contents of a single register onto the stack (PUSH)
    -   Syntax: 0xE0 0x01 0x00 0x00
    -   Example: PUSH R1
        -   Push the contents of R1 onto the stack and decrement SP
    -   Raises ???stack overflow??? exception if SP == 0x0000 before PUSH
-   **0xE1:** Pop value off the stack and store in a register (POP)
    -   Syntax: 0xE1 0x03 0x00 0x00
    -   Example: POP R3
        -   Pop the top value V off the stack, store V in R3, and increment SP
    -   Raises ???stack empty??? exception if SP == 0x0200 before POP
-   **0xE2:** Return from Subroutine (RTS)
    -   Syntax: 0xE2 0x00 0x00 0x00
    -   Example: RTS
        -   Pop the top value off the stack, using it to set the program counter.
            Assumes the value on the top of the stack is the address of an instruction
            following a JSR.  Fails if the top value is a value in the range
            [0x00000, 0x1ffe], which is stack space, or the value is not divisible by
            4, which is a misaligned address for code.



### MISCELLANEOUS

-   **0xFE:** HALT
    -   Syntax: 0xFE 0xFF 0xFE 0xFF
    -   Example: HALT
        -   Stop program execution
-   **0xFF:** NOP
    -   Syntax: 0xFF 0xFF 0xFF 0xFF
    -   Example: NOP
        -   Do nothing until the next instruction cycle

