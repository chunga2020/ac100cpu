.PHONY: tests
tests:
	find . -name '*.bin' -exec rm {} \;
	$(MAKE) -C tests/
	find . -name '*.bin' -exec rm {} \;
