#!/usr/bin/env bash

# clean everything:
rm -rf dist build */*.egg-info *.egg-info

# build:
python setup.py sdist

# upload to pypi:
twine upload dist/*