#!/usr/bin/env bash

set -e

. $(dirname "${0}")/../.env

if [[ -z "$1" ]]; then
    echo "Missing test-name argument"
    exit 1
elif [[ "$1" == "single" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
elif [[ "$1" == "full" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
elif [[ "$1" == "long" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
elif [[ "$1" == "short" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
else
    TEST_NAME=$1
    shift
fi

MODES=()
RUNS=()
#CORES=("cv32e40p" "cva6")
CORES=("cv32e40p")
while [ "$#" -gt 0 ];
do
    arg="$1"
    if [ "$arg" == "single" ]; then
        MODES+=("single")
    elif [ "$arg" == "full" ]; then
        MODES+=("full")
    elif [ "$arg" == "long" ]; then
        RUNS+=("long")
    elif [ "$arg" == "short" ]; then
        RUNS+=("short")
    else
        echo "Unknown test argument"
        exit 1
    fi
    shift
done

TEST_DIR=${PSW_RESULTS}/${TEST_NAME}
BLOCK_LIST_DIR=${PSW_WORKSPACE}/BLOCK_LISTS

trap "echo -e '\n[!] Script aborted by user.'; exit 1" INT

MARKER=".completed"
rm -f "${TEST_DIR}/$MARKER"

for core in "${CORES[@]}"; do

    SRC_DIR=${PSW_M2ISAR_PERF}/out/${core^^}_DSE/code/block_sched/${core^^}_DSE
    VAR_DIR=${PSW_SWEVAL_LIB}/libs/backends/variants/${core^^}_DSE/

    for run in "${RUNS[@]}"; do

        if [[ "$run" == "long" ]]; then
            run_key="_long"
        elif [[ "$run" == "short" ]]; then
            run_key=""
        else
            echo "Unexpected run"
            exit 1
        fi

        # Create run-dir and copy overview script
        run_dir=${TEST_DIR}/${core}/${run}
        mkdir -p "$run_dir"
        cp ${PSW_RESULTS}/scripts/overview.py ${run_dir}

        # Run base-simulations (ETISS, BlocExt, PerfSim)
        for bm in "${PSW_EMBENCH[@]}"; do

            echo "Running base-simulations for ${core} ${run} ${bm}"

            target_dir=${run_dir}/${bm} 
            mkdir -p "$target_dir"

            echo " >> Block-Extractor"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -bext > "$target_dir/DUMP_BlockExt.txt"
            echo " >> ETISS"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -np > "$target_dir/DUMP_ETISS.txt"
            echo " >> PerfSim"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" > "$target_dir/DUMP_PerfSim.txt"
            echo " >> PerfSim (void)"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -v > "$target_dir/DUMP_PerfSim_void.txt"

        done # for bm

        # Run MAP-Explorer simulations
        for mode in "${MODES[@]}"; do

            if [[ "$mode" == "single" ]]; then
                T1=0
                T2=0
                T3=0
            elif [[ "$mode" == "full" ]]; then
                T1=4
                T2=4
                T3=3
            else
                echo "NO VALID MODE SPECIFIED FOR MAP_EXPLORER TEST"
                exit 1
            fi

            # Compile MAP_EXPLORER once for correct number of combinations
            source ${PSW_M2ISAR_PERF}/venv/bin/activate
            python ${PSW_M2ISAR_PERF}/m2isar_perf/run.py "${PSW_CORE_PERF_DSL}/${core^^}_DSE.corePerfDsl" -b "${BLOCK_LIST_DIR}/${core^^}_DSE_CRC32_BlockList.json" "-t1=${T1}" "-t2=${T2}" "-t3=${T3}"
            cp ${SRC_DIR}/include/* ${VAR_DIR}/include
            cp -r ${SRC_DIR}/src/* ${VAR_DIR}/src
            ${PSW_PERF_SIM}/rebuild.sh

            for bm in "${PSW_EMBENCH[@]}"; do

                target_dir=${run_dir}/${bm}

                echo "Running MAP-Explorer simulations for ${core} ${run} ${mode} ${bm}"
                source ${PSW_M2ISAR_PERF}/venv/bin/activate
                echo " >> M2ISAR-Perf"
                python ${PSW_M2ISAR_PERF}/m2isar_perf/run.py "${PSW_CORE_PERF_DSL}/${core^^}_DSE.corePerfDsl" -b "${BLOCK_LIST_DIR}/${core^^}_DSE_${bm^^}${run_key^^}_BlockList.json" "-t1=${T1}" "-t2=${T2}" "-t3=${T3}" > "$target_dir/DUMP_M2ISAR-Perf_${mode}.txt"
                cp -r ${SRC_DIR}/src/block_schedules/* ${VAR_DIR}/src/block_schedules
                echo " >> Compiler"
                ${PSW_PERF_SIM}/rebuild.sh > "$target_dir/DUMP_Compile_${mode}.txt"
                echo " >> MAPExplorer"
                "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -map > "$target_dir/DUMP_MAPExplorer_${mode}.txt"
                echo " >> MAPExplorer (void)"
                "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -map -v > "$target_dir/DUMP_MAPExplorer_void_${mode}.txt"

            done # bm
        done # mode
    done #run
done # core

date -Iseconds > "${TEST_DIR}/${MARKER}"