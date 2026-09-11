#!/usr/bin/env bash

set -e

. $(dirname "${0}")/../.env

TEST_DIR=${PSW_RESULTS_BASE}

#CORES=("cv32e40p" "cva6")
CORES=("cva6")
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

            echo "Running PerfSim for ${core} ${run_name} ${bm}"

            target_dir=$TEST_DIR/$core/$run_name/$bm 
            mkdir -p "$target_dir"

            #"${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run}" --core "${core}" > "$target_dir/DUMP_PerfSim.txt"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run}" --core "${core}" > "$target_dir/DUMP_PerfSim.txt"

        done # for bm
    done # for len
done # for core