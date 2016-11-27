.PHONY: all all-platforms test test-all-platforms install install-requirements install-requirements-tests virtualenv clean

TEST?=${PWD}/test_acspec

RESET=\033[0m
YELLOW=\033[0;33m

all: install install-requirements-tests

all-platforms:
	$(MAKE) all
	$(MAKE) all PYTHON=python3

test: virtualenv
	${VIRTUALENV_DIR}/bin/py.test -vv -m 'not ignore' "${TEST}"

test-all-platforms:
	$(MAKE) test
	$(MAKE) test PYTHON=python3

install: install-requirements
	${VIRTUALENV_DIR}/bin/python setup.py develop

install-requirements: virtualenv
	${VIRTUALENV_DIR}/bin/pip install --upgrade pip
	${VIRTUALENV_DIR}/bin/pip install -r requirements.txt

install-requirements-tests: install
	${VIRTUALENV_DIR}/bin/pip install -r requirements-tests.txt

virtualenv:
ifeq ($(PYTHON),python3)
	@echo "$(YELLOW)Execute with virtualenv for ${PYTHON}$(RESET)"
	$(eval VIRTUALENV_DIR := ${PWD}/env3)
	test -d ${VIRTUALENV_DIR} || virtualenv -p python3 ${VIRTUALENV_DIR}
else
	@echo "$(YELLOW)Execute with default virtualenv$(RESET)"
	$(eval VIRTUALENV_DIR := ${PWD}/env)
	test -d ${VIRTUALENV_DIR} || virtualenv ${VIRTUALENV_DIR}
endif

clean:
	git clean -df
