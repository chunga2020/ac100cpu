# verbose output, with output for all tests, no header (unnecessary output)
PYTEST=python -m pytest -vrA --no-header

tests:
	$(PYTEST) test_definitions.py
	$(PYTEST) test_emu_init.py
	$(PYTEST) test_emu_cmd_line_args.py
	$(PYTEST) test_asm.py
