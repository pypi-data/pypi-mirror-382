#!/bin/bash

if [ "$#" -eq 0 ] || [ "$1" == "-h" ]; then
  echo
  echo "Adds, commits and pushes the new Toucan reports in a given folder, with the given report file name (eg README.md)."
  echo
  echo "Usage: ./$(basename "$0") <PROJECT_ROOT> <REPORT_NAME>"
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

GIT_ROOT=$1
REPORT_NAME=$2

cd "${GIT_ROOT}" || exit

find . \( -name "${REPORT_NAME}" -o -name "previous_days.csv" \) -print0 | xargs -0 git add
git commit -m "[Toucan] Update Toucan reports for $(date +%Y-%m-%d)"
git push
