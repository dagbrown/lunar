
python_files=$(shell ls -1 *.py)

all:
	for file in $(python_files); do \
		python -m py_compile $$file; \
	done
