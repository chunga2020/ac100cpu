# AC100CPU: A 16-bit CPU architecture implemented in Python

The inspiration and basic instruction set design for the AC100 came from
[https://www.youtube.com/playlist?list=PLxLxbi4e2mYGvzNw2RzIsM_rxnNC8m2Kz]().
Details of the architecture, such as the mnemonics and any extra opcodes, are
my own design.

# How to Run
To run the tests, run `pip install -r requirements.txt`.  Then, from the 
project root directory, run `make`.

To run the assembler, run `python -m src.ac100asm <source>`.  To run the
emulator, run `python -m src.ac100 <binary>`.  In both cases, pass `-h` or
`--help` to see available options.

## Architecture Details
See `isa_notes.md` or `isa_notes.org`.
