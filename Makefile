.PHONY: tests
tests:
	find . -name '*.bytecode' -exec rm {} \;
	$(MAKE) -C tests/
	find . -name '*.bytecode' -exec rm {} \;
