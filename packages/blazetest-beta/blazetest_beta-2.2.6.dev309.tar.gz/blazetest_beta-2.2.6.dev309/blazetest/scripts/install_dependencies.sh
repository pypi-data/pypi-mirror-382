#!/bin/bash

if [ -f requirements.txt ]; then
  echo "Installing dependencies using pip > requirements.txt"
  python -m pip install --upgrade pip -q;
  python -m pip install -r requirements.txt;
  echo "Dependencies installed using pip have been installed"
elif [ -f pyproject.toml ]; then
  echo "Installing dependencies using poetry > pyproject.toml"
  python -m pip install poetry -q;
  poetry install;
  echo "Dependencies using poetry have been installed"
elif [ -f Pipfile ]; then
  echo "Installing dependencies using pipenv > Pipfile"
  python -m pip install pipenv -q;
  pipenv install --system --deploy --ignore-pipfile;
  echo "Dependencies using pipenv have been installed"
else
  echo "Error: No dependency management files found.";
  exit 1;
fi
