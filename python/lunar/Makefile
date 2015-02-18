python_files=$(shell ls -1 *.py)

PYC_FILES=__init__.pyc config.pyc create_module_index.pyc modules.pyc moonbase.pyc pkgdb.pyc

all: $(PYC_FILES)

%.pyc: %.py
	python -m py_compile $<

__init__.pyc: __init__.py
config.pyc: config.py
create_module_index.pyc: create_module_index.py
modules.pyc: modules.py
moonbase.pyc: moonbase.py
pkgdb.pyc: pkgdb.py
