#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

rm -rf ../pydantic-fhir
poetry run fhirzeug  --output-directory ../pydantic-fhir --generator python_pydantic
cd ../pydantic-fhir
poetry install
poetry run flake8 --select=F811 pydantic_fhir/r4.py
poetry run pytest tests -vv
