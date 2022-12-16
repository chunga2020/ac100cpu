# output for all non-passed tests only, no header
PYTEST=python -m pytest -ra --no-header

tests:
	$(PYTEST) test_definitions.py
	$(PYTEST) test_emu_init.py
	$(PYTEST) test_emu_cmd_line_args.py
	$(PYTEST) test_asm.py
	$(PYTEST) test_asm_instructions_pass.py
