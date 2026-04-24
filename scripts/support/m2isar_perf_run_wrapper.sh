#!/bin/bash

set -e

exe="python3 ${PSW_M2ISAR_PERF}/m2isar_perf/run.py"

source ${PSW_M2ISAR_PERF}/venv/bin/activate
echo $exe $*
$exe $*
deactivate
