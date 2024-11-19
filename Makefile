include Python.mk
PROJECT	= gmail
COV_FAIL_UNDER = 96
lint :: mypy
doc :: README.md
