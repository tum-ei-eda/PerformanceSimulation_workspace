#!/bin/bash

set -e

. $(dirname "${0}")/../.env

TARGET_SW=$1
shift

CMD_OPTIONS=""
CORE_SPECIFIED=0

while [ "$#" -gt 0 ];
do
    arg="$1"
    if [ "$arg" = "cv32e40p" ] && [ ${CORE_SPECIFIED} == 0 ]; then
	CMD_OPTIONS="${CMD_OPTIONS} --core cv32e40p"
	CORE_SPECIFIED=1
    elif [ "$arg" = "cva6" ] && [ ${CORE_SPECIFIED} == 0 ]; then
	CMD_OPTIONS="${CMD_OPTIONS} --core cva6"
	CORE_SPECIFIED=1
    else
	CMD_OPTIONS="${CMD_OPTIONS} ${arg}"
    fi
    shift
done

if [ ${CORE_SPECIFIED} == 1 ]; then
    ${PSW_SCRIPTS_SUPPORT}/run_etiss_energy_estimate.py ${TARGET_SW} ${CMD_OPTIONS}
else
    echo "No valid core specified!"
fi