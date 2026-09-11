#!/usr/bin/env bash

set -e

. $(dirname "${0}")/../.env

BLOCK_LIST_DIR=${PSW_WORKSPACE}/BLOCK_LISTS

#CORES=("cv32e40p" "cva6")
#RUNS=("" "_typ" "_long")

CORES=("cva6")
RUNS=("_typ")

trap "echo -e '\n[!] Script aborted by user.'; exit 1" INT

for core in "${CORES[@]}"; do
    for run in "${RUNS[@]}"; do
        for bm in "${PSW_EMBENCH[@]}"; do

            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run}" --core "${core}" -bext
            mv "./${core^^}_DSE_BlockList.json" "${BLOCK_LIST_DIR}/${core^^}_DSE_${bm^^}${run^^}_BlockList.json"

        done # for bm
    done # for len
done # for core