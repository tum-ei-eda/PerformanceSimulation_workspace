# 
#  Copyright 2026 Chair of EDA, Technical University of Munich
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
# 	 http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# 

from pathlib import Path
import re
import json
import os
import matplotlib.pyplot as plt

################################ READ_OUT INFO ################################

readoutDict = {
    'BlockExt': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'Compile_single': {
        'time_key': "Done rebuilding ETISS-PerfSim. Time spend:",
        'time_unit': "ms",
        'time_factor': 1000.0
        },
    'Compile_full': {
        'time_key': "Done rebuilding ETISS-PerfSim. Time spend:",
        'time_unit': "ms",
        'time_factor': 1000.0
        },
    'ETISS': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'M2ISAR-Perf_single': {
        'time_key': "Total execution time M2ISAR-Perf:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'M2ISAR-Perf_full': {
        'time_key': "Total execution time M2ISAR-Perf:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'MAPExplorer_single': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'MAPExplorer_full': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'MAPExplorer_void_single': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'MAPExplorer_void_full': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'PerfSim': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'PerfSim_void': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        }
}

################################ GLOBAL VARIABLES ################################

timingResults = {
    'BlockExt': [], 
    'Compile_single': [],
    'Compile_full': [],
    'M2ISAR-Perf_single': [],
    'M2ISAR-Perf_single_Matrix-Gen': [],
    'M2ISAR-Perf_single_Matrix-Opt': [],
    'M2ISAR-Perf_full': [],
    'M2ISAR-Perf_full_Matrix-Gen': [],
    'M2ISAR-Perf_full_Matrix-Opt': [],
    'ETISS': [],
    'MAPExplorer_single': [],
    'MAPExplorer_full': [],
    'MAPExplorer_void_single': [],
    'MAPExplorer_void_full': [],
    'PerfSim': [],
    'PerfSim_void': []
}

ccResults = {
    'MAPExplorer_single': [],
    'PerfSim': []
}

numInstr = []
numVariants = None

################################ FILE READOUT ################################

dirPath = Path(__file__).resolve().parent

benchmarkVariant = dirPath.name
core = dirPath.parent.name
testName = dirPath.parent.parent.name

subDirs = [p for p in dirPath.iterdir() if p.is_dir()]
subDirs.sort(key=lambda x: x.name)
benchmarks = [p.name for p in subDirs]

for subDir_i in subDirs:

    dumps = [d for d in subDir_i.iterdir() if d.is_file()]
    dumps = [d for d in dumps if d.name.startswith("DUMP")]

    for dump_i in dumps:

        dumpName = dump_i.name.replace("DUMP_","").replace(".txt","")

        with dump_i.open('r') as f:
            text = f.read()

        # Readout timing for all dump files
        keyString = readoutDict[dumpName]['time_key']
        unit = readoutDict[dumpName]['time_unit']
        factor = readoutDict[dumpName]['time_factor']

        match = re.search(rf"{keyString}\s*([0-9]*\.?[0-9]+)\s*{unit}", text)
        if match:
            timingResults[dumpName].append(float(match.group(1))/factor)
        else:
            raise RuntimeError(f"Failed to find execution time in {dump_i.name}")
        
        # Read out sub-timings for M2ISAR-Perf
        if dumpName.startswith("M2ISAR-Perf"):
            subs = ['Matrix-Gen', 'Matrix-Opt']
            for s in subs:
                keyString = f"{s} Time:"

                match = re.search(rf"{keyString}\s*([0-9]*\.?[0-9]+)\s*s", text)
                if match:
                    timingResults[(dumpName + "_" + s)].append(float(match.group(1)))
                else:
                    raise RuntimeError(f"Failed to find execution time for {s} in {dump_i.name}")
                
        # For PerfSim read out CC-estimate and instr count
        if dumpName == "PerfSim":

            keyString = " >> Estimated number of processor cycles:"
            match = re.search(rf"{re.escape(keyString)}\s*([0-9]*\.?[0-9]+)", text)
            if match:
                ccResults[dumpName].append(int(match.group(1)))
            else:
                raise RuntimeError(f"Failed to find CC estimate in {dump_i.name}")
            
            keyString = " >> Number of instructions:"
            match = re.search(rf"{re.escape(keyString)}\s*([0-9]*\.?[0-9]+)", text)
            if match:
                numInstr.append(int(match.group(1)))
            else:
                raise RuntimeError(f"Failed to find CC estimate in {dump_i.name}")
            
        # Read out CC-estimate for single MAP_Explorer run
        if dumpName == "MAPExplorer_single":
            keyString = "Estimated cycles (Comb_0):"
            match = re.search(rf"{re.escape(keyString)}\s*([0-9]*\.?[0-9]+)", text)
            if match:
                ccResults[dumpName].append(int(match.group(1)))
            else:
                raise RuntimeError(f"Failed to find CC estimate in {dump_i.name}")
            
        # Read out number of variants if full sim present
        if dumpName == "MAPExplorer_full":
            numVar = 0
            with dump_i.open('r') as f:
                for line in f:
                    match = re.search(r'Comb_(\d+)', line)
                    if match:
                        numVar = max(numVar, (int(match.group(1))+1))
            
            if numVariants is None:
                numVariants = numVar
            elif (numVariants != numVar):
                raise RuntimeError(f"Mismatching number of variants ({numVariants} vs. {numVar}) for {subDir_i.name}")
        
            
################################ CC-Correctness Test ################################

if len(ccResults['MAPExplorer_single']) > 0:

    testPassed = True
    report = ""
    for i, (cc_map, cc_perf) in enumerate(zip(ccResults['MAPExplorer_single'], ccResults['PerfSim'])):
        report += f"{benchmarks[i]} >> MAPExplorer: {cc_map} | PerfSim: {cc_perf}"
        if cc_map != cc_perf:
            report += " >> FAILED\n"
            testPassed = False
        else:
            report += " >> passed\n"
    
    res = f"CC-Correctness Test: {'passed' if testPassed else 'FAILED'}"
    report += "\n" + res +"\n"
    print(res)

    repFile = dirPath / f"ccTest_{testName}_{core}_{benchmarkVariant}.txt"
    with repFile.open('w') as f:
        f.write(report)

else:
    print("CC-Correctness Test: skipped")

################################ SETUP TIMES ################################

width = 0.35
x = list(range(len(benchmarks)))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(8, len(benchmarks) * 1.2), 10), sharex=True)
fig.suptitle(f"{testName} | {core.upper()} | {benchmarkVariant}", fontsize=12)

if len(timingResults['M2ISAR-Perf_single']) > 0:
    m2isarKey = 'M2ISAR-Perf_single'
    m2isar_matGen = timingResults[m2isarKey + '_Matrix-Gen']
    m2isar_matOpt = timingResults[m2isarKey + '_Matrix-Opt']
    m2isar_base = [full - (gen + opt) for full, gen, opt in zip(timingResults[m2isarKey], m2isar_matGen, m2isar_matOpt)]
    comp = timingResults['Compile_single']

    ax1.bar(x, timingResults['BlockExt'], width=width, label='BlockExt', color='#C44E52')
    ax1.bar(x, m2isar_base, width=width, bottom=timingResults['BlockExt'], label='M2ISAR: Base', color='#4C72B0')
    b = [e + m for e, m in zip(timingResults['BlockExt'], m2isar_base)]
    ax1.bar(x, m2isar_matGen, width=width, bottom=b, label='M2ISAR: Matrix-Gen', color='#55A868')
    b = [i + g for i, g in zip(b, m2isar_matOpt)]
    ax1.bar(x, m2isar_matOpt, width=width, bottom=b, label='M2ISAR: Matrix-Opt', color="#B0744C")
    b = [i + o for i, o in zip(b, m2isar_matOpt)]
    ax1.bar(x, comp, width=width, bottom=b, label='Compiler', color="#B04C9F")

    ax1.set_xticks(x)
    ax1.set_xticklabels(benchmarks, rotation=45, ha='right')
    ax1.set_ylabel('Time (s)')
    ax1.set_title('Setup Times (single variant)')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

if len(timingResults['M2ISAR-Perf_full']) > 0:
    m2isarKey = 'M2ISAR-Perf_full'
    m2isar_matGen = timingResults[m2isarKey + '_Matrix-Gen']
    m2isar_matOpt = timingResults[m2isarKey + '_Matrix-Opt']
    m2isar_base = [full - (gen + opt) for full, gen, opt in zip(timingResults[m2isarKey], m2isar_matGen, m2isar_matOpt)]
    comp = timingResults['Compile_full']

    ax2.bar(x, timingResults['BlockExt'], width=width, label='BlockExt', color='#C44E52')
    ax2.bar(x, m2isar_base, width=width, bottom=timingResults['BlockExt'], label='M2ISAR: Base', color='#4C72B0')
    b = [e + m for e, m in zip(timingResults['BlockExt'], m2isar_base)]
    ax2.bar(x, m2isar_matGen, width=width, bottom=b, label='M2ISAR: Matrix-Gen', color='#55A868')
    b = [i + g for i, g in zip(b, m2isar_matOpt)]
    ax2.bar(x, m2isar_matOpt, width=width, bottom=b, label='M2ISAR: Matrix-Opt', color="#B0744C")
    b = [i + o for i, o in zip(b, m2isar_matOpt)]
    ax2.bar(x, comp, width=width, bottom=b, label='Compiler', color="#B04C9F")

    ax2.set_ylabel('Time (s)')
    ax2.set_title(f'Setup Times ({numVariants} variants)')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(dirPath / f"setupTimes_{testName}_{core}_{benchmarkVariant}.png")
#plt.show()

################################ SIMULATION TIMES (single) ################################

if len(timingResults['MAPExplorer_single']) > 0:

    selected_tests = ['PerfSim', 'MAPExplorer_single']
    width = 0.2
    x = list(range(len(benchmarks)))

    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(8, len(benchmarks) * 1.2), 10), sharex=True)
    fig2.suptitle(f"{testName} | {core.upper()} | {benchmarkVariant}", fontsize=12)

    for i, test_i in enumerate(selected_tests):
        offsets = [(xi + (i - 1) * (width + 0.05)) for xi in x]
        ax1.bar(offsets, timingResults['ETISS'], width=width, label='ETISS' if i == 0 else None, color='#C44E52')
        voidKey = test_i + "_void" if (test_i == 'PerfSim') else 'MAPExplorer_void_single'
        voidTime = [v - e for v,e in zip(timingResults[voidKey], timingResults['ETISS'])]
        ax1.bar(offsets, voidTime, width=width, bottom=timingResults['ETISS'], label=f"{test_i}: Setup + Trace")
        compTime = [s - v for s,v in zip(timingResults[test_i], timingResults[voidKey])]
        ax1.bar(offsets, compTime, width=width, bottom=timingResults[voidKey], label=f"{test_i}: Computation")

    ax1.set_xticks(x)
    ax1.set_xticklabels(benchmarks, rotation=45, ha='right')
    ax1.set_ylabel('Time (s)')
    ax1.set_title('Simulation times')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    for i, test_i in enumerate(selected_tests):
        offsets = [(xi + (i - 1) * (width + (width/4))) for xi in x]
        voidKey = test_i + "_void" if (test_i == 'PerfSim') else 'MAPExplorer_void_single'
        compTime = [c - v for c,v in zip(timingResults[test_i], timingResults[voidKey])]
        ax2.bar(offsets, compTime, width=width, label=f"{test_i}: Computation")

    ax2.set_ylabel('Time (s)')
    ax2.set_title('Processing times')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(dirPath / f"simTimes_single_{testName}_{core}_{benchmarkVariant}.png")
    #plt.show()

################################ OVERVIEW TABLE ################################

if len(timingResults['MAPExplorer_full']) > 0:

    # Total counts
    numInstr_tot = 0
    perfSim_simTime_tot = 0
    expTime_tot = 0
    simTime_tot = 0
    setupTime_tot = 0
    totalTime_tot = 0

    # Accumulated counts (for avg.)
    perfSim_mips_acc = 0
    mips_acc = 0
    delta_acc = 0
    speedUp_acc = 0

    # Make benchmark rows
    rows = ""
    for i, bm_i in enumerate(benchmarks):

        n = numInstr[i]
        rows += f"{bm_i} & {n} &"

        perfSim_simTime = round(timingResults['PerfSim'][i], 2)
        expTime = round(perfSim_simTime*numVariants, 2)
        perfSim_mips = round(((n*numVariants) / 1000000) / expTime, 2)
        rows += f"{perfSim_simTime} & {expTime} & {perfSim_mips} &"

        simTime = round(timingResults['MAPExplorer_full'][i], 2)
        setupTime = round(timingResults['BlockExt'][i] + timingResults['M2ISAR-Perf_full'][i] + timingResults['Compile_full'][i], 2)
        totalTime = round(simTime + setupTime, 2)
        mips = round(((n*numVariants) / 1000000) / totalTime, 2)
        delta = round(expTime - totalTime, 2)
        speedUp = round((expTime / totalTime), 2)
        rows += f"{setupTime} & {simTime} & {totalTime} & {mips} & {delta} & {speedUp}x \\\\\n"

        # Increase total counts
        numInstr_tot += n
        perfSim_simTime_tot += perfSim_simTime
        expTime_tot += expTime
        simTime_tot += simTime
        setupTime_tot += setupTime
        totalTime_tot += totalTime

        # Increase accumulats
        perfSim_mips_acc += perfSim_mips
        mips_acc += mips
        delta_acc += delta
        speedUp_acc += speedUp

    
    # Make "total" row
    total_row = ""
    total_row += f"Total & {numInstr_tot} &"

    perfSim_mips_tot = round(((numInstr_tot*numVariants) / 1000000) / expTime_tot, 2)
    total_row += f"{round(perfSim_simTime_tot,2)} & {round(expTime_tot,2)} & {perfSim_mips_tot} &"

    simTime_tot = round(simTime_tot, 2)
    mips_tot = round(((numInstr_tot*numVariants) / 1000000) / totalTime_tot, 2)
    delta_tot = round(expTime_tot - totalTime_tot, 2)
    speedUp_tot = round((expTime_tot / totalTime_tot), 2)
    total_row += f"{round(setupTime_tot,2)} & {round(simTime_tot,2)} & {round(totalTime_tot,2)} & {mips_tot} & {delta_tot} & {speedUp_tot}x \\\\\n"

    # Make "Avg." row
    avg_row = ""

    numBenchmarks = len(benchmarks)

    num_instr_avg = round(numInstr_tot / numBenchmarks, 2) 
    avg_row += f"Avg. & {num_instr_avg} & "

    perfSim_simTime_avg = round(perfSim_simTime_tot / numBenchmarks, 2)
    expTime_avg = round(expTime_tot / numBenchmarks, 2)
    perfSim_mips_avg = round(perfSim_mips_acc / numBenchmarks, 2)
    avg_row += f"{perfSim_simTime_avg} & {expTime_avg} & {perfSim_mips_avg} &"

    setupTime_avg = round(setupTime_tot / numBenchmarks, 2)
    simTime_avg = round(simTime_tot / numBenchmarks, 2)
    totalTime_avg = round(totalTime_tot / numBenchmarks, 2)
    mips_avg = round(mips_acc / numBenchmarks, 2)
    delta_avg = round(delta_acc / numBenchmarks, 2)
    speedUp_avg = round(speedUp_acc / numBenchmarks, 2)
    avg_row += f"{setupTime_avg} & {simTime_avg} & {totalTime_avg} & {mips_avg} & {delta_avg} & {speedUp_avg}x \\\\\n"


    # Create Table
    tableContent = rf"""
    \documentclass{{article}}
    \usepackage[margin=2cm]{{geometry}}
    \usepackage{{pdflscape}}

    \begin{{document}}
    \begin{{landscape}}

    \begin{{table}}[ht]
    \centering
    \caption{{Results: {testName}, {core.upper()}, {benchmarkVariant}, Variants: {numVariants}}}
    \centering
    \begin{{tabular}}{{c | c | c c c | c c c c c c}}
    \hline
    \multicolumn{{2}}{{c}}{{Benchmarks}} & \multicolumn{{3}}{{c}}{{PerfSim}} & \multicolumn{{6}}{{c}}{{MAPExplorer}}\\
    Name & \#Instr & SimTime (1var) & SimTime (exp.) & MIPS & SetupTime & SimTime & Total & MIPS & $\Delta$ & Speed-Up \\
    \hline
    {rows}
    \hline
    {total_row}
    \hline
    {avg_row}
    \hline
    \end{{tabular}}
    \end{{table}}

    \end{{landscape}}
    \end{{document}}
    """

    texFile = dirPath / f"results_{testName}_{core}_{benchmarkVariant}.tex"
    texFile.write_text(tableContent)

    os.system("pdflatex -output-directory=" + str(dirPath) + " " + str(texFile))    