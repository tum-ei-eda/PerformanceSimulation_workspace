#!/usr/bin/env bash

set -e

. $(dirname "${0}")/../.env

# Select mode
MODE=$1
if [[ "$MODE" == "single" ]]; then
    T1=0
    T2=0
    T3=0
elif [[ "$MODE" == "full" ]]; then
    T1=4
    T2=4
    T3=3
else
    echo "NO VALID MODE SPECIFIED FOR MAP_EXPLORER TEST"
    exit 1
fi
shift

# Select test name
if [[ -z "$1" ]]; then
    TEST_NAME="CURRENT"
else
    TEST_NAME=$1
    shift
fi

TEST_DIR=${PSW_RESULTS}/${TEST_NAME}
BASE_DIR=${PSW_RESULTS_BASE}

BLOCK_LIST_DIR=${PSW_WORKSPACE}/BLOCK_LISTS

echo $BLOCK_LIST_DIR

#CORES=("cv32e40p" "cva6")
CORES=("cv32e40p")
#RUNS=("" "_long")
RUNS=("")

trap "echo -e '\n[!] Script aborted by user.'; exit 1" INT

for core in "${CORES[@]}"; do

    SRC_DIR=${PSW_M2ISAR_PERF}/out/${core^^}_DSE/code/block_sched/${core^^}_DSE
    TARGET_DIR=${PSW_SWEVAL_LIB}/libs/backends/variants/${core^^}_DSE/

    echo $SRC_DIR
    echo $TARGET_DIR

    # Compile MAP_EXPLORER once for correct combination-space
    source ${PSW_M2ISAR_PERF}/venv/bin/activate
    python ${PSW_M2ISAR_PERF}/m2isar_perf/run.py "${PSW_CORE_PERF_DSL}/${core^^}_DSE.corePerfDsl" -b "${BLOCK_LIST_DIR}/${core^^}_DSE_CRC32_BlockList.json" "-t1=${T1}" "-t2=${T2}" "-t3=${T3}"
    cp ${SRC_DIR}/include/* ${TARGET_DIR}/include
    cp -r ${SRC_DIR}/src/* ${TARGET_DIR}/src
    ${PSW_PERF_SIM}/rebuild.sh

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

            # Copy information from base to current test dir
            cp ${BASE_DIR}/${core}/${run_name}/${bm}/* $target_dir

            source ${PSW_M2ISAR_PERF}/venv/bin/activate
            python ${PSW_M2ISAR_PERF}/m2isar_perf/run.py "${PSW_CORE_PERF_DSL}/${core^^}_DSE.corePerfDsl" -b "${BLOCK_LIST_DIR}/${core^^}_DSE_${bm^^}${run^^}_BlockList.json" "-t1=${T1}" "-t2=${T2}" "-t3=${T3}" > "$target_dir/DUMP_M2ISAR-Perf.txt"
            #cp ${SRC_DIR}/include/* ${TARGET_DIR}/include
            cp -r ${SRC_DIR}/src/block_schedules/* ${TARGET_DIR}/src/block_schedules
            ${PSW_PERF_SIM}/rebuild.sh > "$target_dir/DUMP_Compile.txt"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run}" --core "${core}" > "$target_dir/DUMP_MAPExplorer_${MODE}.txt"

        done # for bm
    done # for len
done # for core