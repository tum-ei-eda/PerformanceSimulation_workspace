# PerformanceSimulation_workspace
Example workspace for software performance simulation with ETISS-based performance simulator (WiP!)

## Overview
This is an example workspace for the ETISS-based performance simulator. It contains:
- The ETISS-based performance simulator etiss-perf-sim
- The M2-ISA-R-Perf code generator to adjust the performance models
- The Embench benchmark suite, compiled for the CV32E40P (RV32IM) and CVA6 (RV64IM), as a target-software example
- An extension to support custom dotproduct instructions
- A lightweight energy estimator based on power report data from a commercial tool in statistical mode

## First Time Setup

### Create workspace

Clone this repository and navigate to its top folder. (The given example uses an SSH-based link; adapt if necessary)

      $ git clone git@github.com:tum-ei-eda/PerformanceSimulation_workspace.git <YOUR_WORKSPACE_NAME>
      $ cd <YOUR_WORKSPACE_NAME>

Switch to the performance & energy version with dotproduct support:

      $ git checkout perf_energy_dotp

Initialize required git-submodules:

      $ git submodule update --init --recursive

### Install workspace

Install the workspace by calling:

      $ ./scripts/setup_workspace.sh


## Usage

### Performance Simulation

Example: Run a performance simulation for the embench-crc32 benchmark on the CV32E40P:

      $ ./scripts/run.sh em:crc32 cv32e40p

Example: Run a performance simulation for the embench-ud benchmark on the CVA6 and create a performance-trace:

      $ ./scripts/run.sh em:ud cva6 -tp=<YOUR/TRACE/PATH>

Example: Run an instruction simulation (without performance estimation) for the embench-crc32 benchmark on the CV32E40P:

      $ ./scripts/run.sh em:crc32 cv32e40p -np

### Performance & Energy Simulation

For energy estimation, the following parameters have to be added to defined:
- `-uApr`: path to the power report of commercial tool in statistical mode
- `-uAt`: name of the top module, which should be considered for energy estimation
- `-uAct`: clock cycle duration, considered for energy estimation (in ns)


Example: Run a performance & energy simulation for any custom benchmark on the CVA6:

      $ ./scripts/run_energy.sh custom:<path_to_binary> cva6 -uApr=<path_to_power_rpt> -uAt=ariane -uAct=20


### Code Generation

Example: Generate performance estimator from corePerfDsl description, deploy it and re-install ETISS:

      $ ./scripts/code_gen.sh ./code_gen/descriptions/core_perf_dsl/CV32E40P.corePerfDsl

Example: Generate trace printer from monitor description, deploy it and re-install ETISS:

      $ ./scripts/code_gen.sh ./code_gen/descriptions/monitor_descriptions/InstructionTrace_RV64.json

## Version

The latest release version of this repository is v0.2

It is compatible with the following submodule versions:

| Submodule | Version |
| --------- | ------- |
| etiss-perf-sim | v0.10 |
| M2-ISA-R | WiP |
| M2-ISA-R-Perf | v2.0 |
| etiss_arch_riscv | WiP |
| CorePerfDSL-Examples | v2.0 |
