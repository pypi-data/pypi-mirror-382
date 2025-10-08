#!/bin/bash

if [ "$#" -eq 0 ] || [ "$1" == "-h" ]; then
  echo
  echo "Checkout a given branch and pull latest."
  echo
  echo "Usage: ./$(basename "$0") <PROJECT_ROOT> <BRANCH>"
  echo
  exit 0
elif ! [ "$#" -eq 2 ]; then
  echo
  echo "Expected 2 arguments, got $# instead."
  echo
  echo "Run ./$(basename "$0") -h for more information."
  echo
  exit 1
fi

PROJECT_ROOT=$1
BRANCH=$2

cd "${PROJECT_ROOT}" || exit

git checkout "$BRANCH"
git pull origin "$BRANCH"
