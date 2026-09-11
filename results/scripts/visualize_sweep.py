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
import matplotlib.pyplot as plt

################################ READ_OUT INFO ################################

readoutDict = {
    'BlockExt': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'Compile': {
        'time_key': "Done rebuilding ETISS-PerfSim. Time spend:",
        'time_unit': "ms",
        'time_factor': 1000.0
        },
    'M2ISAR-Perf': {
        'time_key': "Total execution time M2ISAR-Perf:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'MAPExplorer': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'MAPExplorer_isched': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
    'PerfSim': {
        'time_key': "Total execution time:",
        'time_unit': "s",
        'time_factor': 1.0
        },
}

################################ GLOBAL VARIABLES ################################

timingResultsSweep = {
    'MAPExplorer': [],
    'MAPExplorer_isched': []
}

timingResults = {
    'BlockExt': 0,
    'Compile': 0,
    'M2ISAR-Perf': 0,
    'PerfSim': 0
}

numInstr = 0

################################ FILE READOUT ################################

dirPath = Path(__file__).resolve().parent

bmName = dirPath.name
bmVariant = dirPath.parent.name
core = dirPath.parent.parent.name
testName = dirPath.parent.parent.parent.name
print(bmName)
print(bmVariant)
print(core)

dumps = [d for d in dirPath.iterdir() if d.is_file() and d.name.startswith("DUMP_")]

sweepDumps = {}
sweepDumps['MAPExplorer_isched'] = [d for d in dumps if "MAPExplorer_isched" in d.name]
supportDumps = [d for d in dumps if d not in sweepDumps['MAPExplorer_isched']]
sweepDumps['MAPExplorer'] = [d for d in supportDumps if "MAPExplorer" in d.name]
supportDumps = [d for d in supportDumps if d not in sweepDumps['MAPExplorer']]

sweepDumps['MAPExplorer_isched'].sort()
sweepDumps['MAPExplorer'].sort()

# Read out support dumps
for dump_i in supportDumps:
    
    dumpName = dump_i.name.replace("DUMP_", "").replace(".txt", "")

    with dump_i.open("r") as f:
        text = f.read()
    
    keyString = readoutDict[dumpName]['time_key']
    unit = readoutDict[dumpName]['time_unit']
    factor = readoutDict[dumpName]['time_factor']
    
    match = re.search(rf"{keyString}\s*([0-9]*\.?[0-9]+)\s*{unit}", text)
    if match:
        timingResults[dumpName] = (float(match.group(1))/factor)
    else:
        raise RuntimeError(f"Failed to find execution time in {dump_i.name}")

    if dumpName == "PerfSim":
            
        keyString = " >> Number of instructions:"
        match = re.search(rf"{re.escape(keyString)}\s*([0-9]*\.?[0-9]+)", text)
        if match:
            numInstr = (int(match.group(1)))
        else:
            raise RuntimeError(f"Failed to find number of instructions in {dump_i.name}")

# Read out MAPExplorer and MAPExplorer_isched dumps
if len(sweepDumps['MAPExplorer']) != len(sweepDumps['MAPExplorer_isched']):
    raise RuntimeError("Number of MAPExplorer and MAPExplorer_isched dumps do not match")

numVariants = [None]*len(sweepDumps['MAPExplorer'])
for sweep_i in ['MAPExplorer_isched', 'MAPExplorer']:
    
    for i, dump_i in enumerate(sweepDumps[sweep_i]):

        #dumpName = dump_i.name.replace("DUMP_", "").replace(".txt", "")

        numVar = 0
        with dump_i.open("r") as f:
            for line in f:
                match = re.search(r'Comb_(\d+)', line)
                if match:
                    numVar = max(numVar, (int(match.group(1))+1))

        if numVariants[i] is None:
            numVariants[i] = numVar
        else:
            if numVariants[i] != numVar:
                raise RuntimeError(f"Mismatching number of variants in loop {i}")

        with dump_i.open("r") as f:
            text = f.read()

        keyString = readoutDict[sweep_i]['time_key']
        unit = readoutDict[sweep_i]['time_unit']
        factor = readoutDict[sweep_i]['time_factor']

        match = re.search(rf"{keyString}\s*([0-9]*\.?[0-9]+)\s*{unit}", text)
        if match:
            timingResultsSweep[sweep_i].append(float(match.group(1))/factor)
        else:
            raise RuntimeError(f"Failed to find execution time in {dump_i.name}")

################################ CALCULATE DATA ################################

setupTime = timingResults['BlockExt'] + timingResults['M2ISAR-Perf'] + timingResults['Compile']
#setupTime = 10
timing_MAPExplorer_setup = [t + setupTime for t in timingResultsSweep['MAPExplorer']]

timing_perfSim_exp = [n*timingResults['PerfSim'] for n in numVariants]

numInstr_M = float(numInstr / 1000000)

mips_MAPExplorer_setup = [round((numInstr_M*n) / t, 2) for t, n in zip(timing_MAPExplorer_setup, numVariants)]
mips_MAPExplorer_isched = [round((numInstr_M*n) / t, 2) for t, n in zip(timingResultsSweep['MAPExplorer_isched'], numVariants)]
mips_perfSim =  [round((numInstr_M*n) / t, 2) for t, n in zip(timing_perfSim_exp, numVariants)]

################################ PLOT SWEEP ################################

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
fig.suptitle(f"{testName} | {core.upper()} | {bmName}({bmVariant})", fontsize=12)

# -- Runtime plot --
ax1.plot(numVariants, timing_MAPExplorer_setup, marker='x', label='MAPExplorer')
ax1.plot(numVariants, timingResultsSweep['MAPExplorer_isched'], marker='o', label='MAPExplorer (instr-sched)')
ax1.plot(numVariants, timing_perfSim_exp, linestyle=':', marker='.', label='PerfSim. (extrapolated)')
ax1.set_ylabel("Runtimes [s]")
ax1.axvspan(1, 16, alpha=0.1, label='I\$')
ax1.axvspan(16, 256, alpha=0.2, label='D\$')
ax1.axvspan(256, max(numVariants), alpha=0.3, label='Br.Pred')
ax1.legend(loc='upper left')
ax1.grid(True)

ax2.plot(numVariants, mips_MAPExplorer_setup, marker='x', label='MAPExplorer')
ax2.plot(numVariants, mips_MAPExplorer_isched, marker='o', label='MAPExplorer (instr-sched.)')
ax2.plot(numVariants, mips_perfSim, linestyle=':', marker='.', label='PerfSim. (extrapolated)')
ax2.set_xlabel("Num. of variants")
ax2.set_ylabel("Simulation throughput [MIPS]")
ax2.axvspan(1, 16, alpha=0.1, label='I\$')
ax2.axvspan(16, 256, alpha=0.2, label='D\$')
ax2.axvspan(256, max(numVariants), alpha=0.3, label='Br.Pred')
ax2.set_xscale("log", basex=2)
ax2.legend(loc='upper left')
ax2.grid(True)

plt.savefig("sweeptest.pdf", bbox_inches='tight')