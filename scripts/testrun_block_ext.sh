#!/usr/bin/env bash

set -e

. $(dirname "${0}")/../.env

TEST_DIR=${PSW_RESULTS_BASE}
BLOCK_LIST_DIR=${PSW_WORKSPACE}/BLOCK_LISTS

CORES=("cv32e40p" "cva6")
RUNS=("" "_long")
#RUNS=("")

trap "echo -e '\n[!] Script aborted by user.'; exit 1" INT

for core in "${CORES[@]}"; do
    for run in "${RUNS[@]}"; do
        for bm in "${PSW_EMBENCH[@]}"; do

            if [[ "$run" == "_long" ]]; then
                run_name="long"
            else
                run_name="short"
            fi

            echo "Running BlockExtractor for ${core} ${run_name} ${bm}"

            target_dir=$TEST_DIR/$core/$run_name/$bm 
            mkdir -p "$target_dir"

            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run}" --core "${core}" -bext > "$target_dir/DUMP_BlockExt.txt"
            mv "./${core^^}_DSE_BlockList.json" "${BLOCK_LIST_DIR}/${core^^}_DSE_${bm^^}${run^^}_BlockList.json"

        done # for bm
    done # for len
done # for core