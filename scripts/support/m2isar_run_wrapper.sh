#!/bin/bash

set -e

source ${PSW_M2ISAR}/venv/bin/activate
echo $*
$*
deactivate
