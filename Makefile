init:
	virtualenv -p python3.5 env
	env/bin/pip install -U setuptools
	env/bin/pip install -r requirements.txt

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*__pycache__' -exec rm --force --recursive {} +

clean-build:
	rm --force --recursive build/

clean-all: clean-pyc clean-build
	rm --force --recursive swagger_client/
	rm --force --recursive env/

build:
	env/bin/python3.5 setup.py build

test:
	env/bin/python3.5 tests/test.py
