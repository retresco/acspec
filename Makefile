.PHONY: all test virtualenv install install-requirements install-requirements-tests clean

VIRTUALENV_DIR=${PWD}/env
PIP=${VIRTUALENV_DIR}/bin/pip
PYTHON=${VIRTUALENV_DIR}/bin/python

all: install install-requirements-tests

test:
	${VIRTUALENV_DIR}/bin/py.test -vv -m 'not ignore' "test_acspec"

virtualenv:
	if [ ! -e ${VIRTUALENV_DIR}/bin/pip ]; then virtualenv ${VIRTUALENV_DIR} --no-site-packages; fi

install: install-requirements
	${PYTHON} setup.py develop

install-requirements: virtualenv
	${PIP} install --upgrade pip
	${PIP} install -r requirements.txt

install-requirements-tests: install
	${PIP} install -r requirements-tests.txt

clean:
	git clean -df
