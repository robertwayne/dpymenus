#!/usr/bin/env bash

rm -rf build
python setup.py sdist bdist_wheel
python -m twine upload --skip-existing dist/*
