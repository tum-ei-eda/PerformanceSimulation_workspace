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
elif [[ "$1" == "fullfull" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
elif [[ "$1" == "long" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
elif [[ "$1" == "short" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
elif [[ "$1" == "typ" ]]; then
    echo "Missing test-name argument (must be first argument)"
    exit 1
else
    TEST_NAME=$1
    shift
fi

RUNS=("typ")
CORES=("cv32e40p" "cva6")

TEST_DIR=${PSW_RESULTS}/${TEST_NAME}
BLOCK_LIST_DIR=${PSW_WORKSPACE}/BLOCK_LISTS

trap "echo -e '\n[!] Script aborted by user.'; exit 1" INT

mkdir -p "$TEST_DIR"
MARKER=".completed"
rm -f "${TEST_DIR}/$MARKER"

for core in "${CORES[@]}"; do

    SRC_DIR=${PSW_M2ISAR_PERF}/out/${core^^}_DSE/code/block_sched/${core^^}_DSE
    VAR_DIR=${PSW_SWEVAL_LIB}/libs/backends/variants/${core^^}_DSE

    if [[ "$core" == "cv32e40p" ]]; then
        VI=32
        VD=32
        VB=8
    elif [[ "$core" == "cva6" ]]; then
        VI=32
        VD=32
        VB=4
    else
        echo "NO VALID CORE SPECIFIED FOR MAP_EXPLORER TEST"
        exit 1
    fi


    for run in "${RUNS[@]}"; do
        run_key="_typ"

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
            mv "./${core^^}_DSE_BlockList.json" "${BLOCK_LIST_DIR}/${core^^}_DSE_${bm^^}${run_key^^}_BlockList.json"
            echo " >> ETISS"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -np > "$target_dir/DUMP_ETISS.txt"
            echo " >> PerfSim"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" > "$target_dir/DUMP_PerfSim.txt"
            #echo " >> PerfSim (void)"
            #"${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -v > "$target_dir/DUMP_PerfSim_void.txt"

        done # for bm


        # Compile MAP_EXPLORER once for correct number of combinations
        source ${PSW_M2ISAR_PERF}/venv/bin/activate
        python3.10 ${PSW_M2ISAR_PERF}/m2isar_perf/run.py "${PSW_CORE_PERF_DSL}/${core^^}_DSE.corePerfDsl" -b "${BLOCK_LIST_DIR}/${core^^}_DSE_CRC32_BlockList.json" "-vi=${VI}" "-vd=${VD}" "-vb=${VB}"
        cp ${SRC_DIR}/include/* ${VAR_DIR}/include
        cp -r ${SRC_DIR}/src/* ${VAR_DIR}/src
        ${PSW_PERF_SIM}/rebuild.sh

        for bm in "${PSW_EMBENCH[@]}"; do

            target_dir=${run_dir}/${bm}

            echo "Running MAP-Explorer simulations for ${core} ${run} ${bm}"
            source ${PSW_M2ISAR_PERF}/venv/bin/activate
            echo " >> M2ISAR-Perf"
            rm ${VAR_DIR}/src/block_schedules/*
            python3.10 ${PSW_M2ISAR_PERF}/m2isar_perf/run.py "${PSW_CORE_PERF_DSL}/${core^^}_DSE.corePerfDsl" -b "${BLOCK_LIST_DIR}/${core^^}_DSE_${bm^^}${run_key^^}_BlockList.json" "-vi=${VI}" "-vd=${VD}" "-vb=${VB}" > "$target_dir/DUMP_M2ISAR-Perf.txt"
            cp -r ${SRC_DIR}/src/block_schedules/* ${VAR_DIR}/src/block_schedules
            echo " >> Compiler"
            ${PSW_PERF_SIM}/rebuild.sh > "$target_dir/DUMP_Compile.txt"
            echo " >> MAPExplorer"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -map > "$target_dir/DUMP_MAPExplorer.txt"
            #echo " >> MAPExplorer (void)"
            #"${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -map -v > "$target_dir/DUMP_MAPExplorer_void_${mode}.txt"
            echo " >> MAPExplorer (instruction_scheduling)"
            "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${bm}${run_key}" --core "${core}" -map -isched > "$target_dir/DUMP_MAPExplorer_isched.txt"

        done # bm

    done #run
done # core

date -Iseconds > "${TEST_DIR}/${MARKER}"