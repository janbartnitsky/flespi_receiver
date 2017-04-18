init: get-swagger-client
	virtualenv -p python3.5 env
	env/bin/pip install -r requirements.txt

get-swagger-client:
	wget --no-check-certificate $(shell curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"spec": {}, "options": {}, "swaggerUrl": "https://flespi.io/gw/api.json"}' 'http://generator.swagger.io/api/gen/clients/python' | jq -r '.link') -O swagger-client.zip
	unzip swagger-client.zip > /dev/null
	rm -r swagger_client -f
	mv python-client/swagger_client/ .
	rm -r python-client/ swagger-client.zip -f

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
