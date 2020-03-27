#!/bin/bash

if ! python3 -c "import virtualenv" &> /dev/null; then
	pip3 install virtualenv
fi

if ! [ -d ".tests" ]; then
	echo "Virtualenv not found, setting up."
	virtualenv .tests
	chmod +x .tests/bin/activate
	source .tests/bin/activate
	pip3 install -r  requirements.txt
else
	source .tests/bin/activate
fi

flake8 --exit-zero --max-complexity=10 ../launcher.py ../cogs/**.py
isort --check -rc ../launcher.py ../cogs/**.py
