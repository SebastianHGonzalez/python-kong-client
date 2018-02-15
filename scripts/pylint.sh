#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
pylint src/
echo "pylint OK :)"


