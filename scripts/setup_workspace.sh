#!/bin/bash

set -e

# Source environment
. $(dirname "${0}")/../.env

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 (Currently required by M2-ISA-R) is not installed on this system. Install it and try again."
    exit 1
fi
which python3

# Setup etiss-perf-sim
${PSW_PERF_SIM}/setup_simulator.sh

# Setup M2-ISA-R
cd ${PSW_M2ISAR}
python3 -m venv venv
source venv/bin/activate
pip install -e .
deactivate

# Setup M2-ISA-R-Perf
cd ${PSW_M2ISAR_PERF}
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
