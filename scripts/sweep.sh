set -e

. $(dirname "${0}")/../.env

TEST_NAME=$1
shift

BENCHMARK=$1
shift

BENCHMARK="${BENCHMARK}_long"

#CORE="cv32e40p"
CORE="cva6"

TEST_DIR=${PSW_RESULTS}/${TEST_NAME}
TARGET_DIR=${TEST_DIR}/${CORE}/long/${BENCHMARK}

BLOCK_LIST_DIR=${PSW_WORKSPACE}/BLOCK_LISTS
BLOCK_LIST=${BLOCK_LIST_DIR}/${CORE^^}_DSE_${BENCHMARK^^}_BlockList.json

CORE_PERF_DSL=${PSW_CORE_PERF_DSL}/${CORE^^}_DSE.corePerfDsl

SRC_DIR=${PSW_M2ISAR_PERF}/out/${CORE^^}_DSE/code/block_sched/${CORE^^}_DSE
VAR_DIR=${PSW_SWEVAL_LIB}/libs/backends/variants/${CORE^^}_DSE

trap "echo -e '\n[!] Script aborted by user.'; exit 1" INT

mkdir -p "$TARGET_DIR"
cp ${PSW_RESULTS}/scripts/visualize_sweep.py ${TARGET_DIR}
MARKER=".completed"
rm -f "${TEST_DIR}/$MARKER"

# # Perf-Sim reference simulation
# echo " >> PerfSim"
# "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" > "$TARGET_DIR/DUMP_PerfSim.txt"


#for i in $(seq 0 5); do
#    iVar=$((2**i))
#    source "${PSW_M2ISAR_PERF}/venv/bin/activate"
#    python3.10 "${PSW_M2ISAR_PERF}/m2isar_perf/run.py" "${CORE_PERF_DSL}" "-b=${BLOCK_LIST}" -vi=${iVar} -vd=1 -vb=1
#    cp "$SRC_DIR/include/"* "${VAR_DIR}/include/"
#    cp -r "$SRC_DIR/src/"* "${VAR_DIR}/src/"
#    ./etiss-perf-sim/rebuild.sh
#    #echo " >> MAPExplorer (${i},0,0)"
#    #"${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -map > "$TARGET_DIR/DUMP_MAPExplorer_${i}_0_0.txt"
#    echo " >> MAPExplorer (instruction_scheduling) (${i},0,0)"
#    "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -map -isched > "$TARGET_DIR/DUMP_MAPExplorer_isched_${i}_0_0.txt"
#done

#for i in $(seq 1 5); do
#    dVar=$((2**i))
#    source "${PSW_M2ISAR_PERF}/venv/bin/activate"
#    python3.10 "${PSW_M2ISAR_PERF}/m2isar_perf/run.py" "${CORE_PERF_DSL}" "-b=${BLOCK_LIST}" -vi=32 -vd=${dVar} -vb=1
#    cp "$SRC_DIR/include/"* "${VAR_DIR}/include/"
#    cp -r "$SRC_DIR/src/"* "${VAR_DIR}/src/"
#    ./etiss-perf-sim/rebuild.sh
#    #echo " >> MAPExplorer (5,${i},0)"
#    #"${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -map > "$TARGET_DIR/DUMP_MAPExplorer_5_${i}_0.txt"
#    echo " >> MAPExplorer (instruction_scheduling) (5,${i},0)"
#    "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -map -isched > "$TARGET_DIR/DUMP_MAPExplorer_isched_5_${i}_0.txt"
#done

for i in $(seq 4 4); do
    bVar=$((2**i))
    source "${PSW_M2ISAR_PERF}/venv/bin/activate"
    python3.10 "${PSW_M2ISAR_PERF}/m2isar_perf/run.py" "${CORE_PERF_DSL}" "-b=${BLOCK_LIST}" -vi=32 -vd=32 -vb=${bVar}
    cp "$SRC_DIR/include/"* "${VAR_DIR}/include/"
    cp -r "$SRC_DIR/src/"* "${VAR_DIR}/src/"
    ./etiss-perf-sim/rebuild.sh
    #echo " >> MAPExplorer (5,5,${i})"
    #"${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -map > "$TARGET_DIR/DUMP_MAPExplorer_5_5_${i}.txt"
    echo " >> MAPExplorer (instruction_scheduling) (5,5,${i})"
    "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -map -isched > "$TARGET_DIR/DUMP_MAPExplorer_isched_5_5_${i}.txt"
done

# # Gather setup time for one build (number of variants should not affect setup-time)
# echo " >> Block-Extractor"
# "${PSW_SCRIPTS_SUPPORT}/run_helper.py" "em:${BENCHMARK}" --core "${CORE}" -bext > "$TARGET_DIR/DUMP_BlockExt.txt"
# echo " >> M2ISAR-Perf"
# source "${PSW_M2ISAR_PERF}/venv/bin/activate"
# python3.10 "${PSW_M2ISAR_PERF}/m2isar_perf/run.py" "${CORE_PERF_DSL}" "-b=${BLOCK_LIST}" -vi=32 -vd=32 -vb=16 > "$TARGET_DIR/DUMP_M2ISAR-Perf.txt"
# cp -r ${SRC_DIR}/src/block_schedules/* ${VAR_DIR}/src/block_schedules
# echo " >> Compiler"
# ${PSW_PERF_SIM}/rebuild.sh > "$TARGET_DIR/DUMP_Compile.txt"

date -Iseconds > "${TEST_DIR}/${MARKER}"
