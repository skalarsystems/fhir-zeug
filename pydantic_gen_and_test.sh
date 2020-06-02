#!/bin/bash

rm -rf ../pydantic-fhir
poetry run fhirzeug  --output-directory ../pydantic-fhir --generator python_pydantic
cd ../pydantic-fhir
poetry run pytest tests -v