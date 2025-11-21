#!/usr/bin/env python3
import argparse
import os
import sys

# Read input arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("targetSW", help="Target software handle (e.g.: dhry, em:cubic)")
argParser.add_argument("-c", "--core", help="Target core architecture [cv32e40p | cva6]")
argParser.add_argument("-uApr", "--uArchPowerreport", help="Full path to commercial power report of core architecture")
argParser.add_argument("-uAt", "--uArchTopmodule", help="Name of top module of core in power report")
argParser.add_argument("-uAct", "--uArchCycletime", help="Cycle time of core in ns")
args, args_passThrough = argParser.parse_known_args()

sim_args = ""

# Resolve CORE
if args.core is None:
   sys.exit("FATAL: Called support-script run_helper.py without specifying a core")
else:
   sim_args += " --core " + args.core

# Resolve TARGET_SW
targetSW_failed = False
targetSW_prefix = "PSW_TARGETSW_" + args.core.upper() + "_"
if len(split:=args.targetSW.split(":")) == 1:
   if split[0] == "dhry":
      targetSW = os.environ.get(targetSW_prefix + "DHRYSTONE_DEFAULT")
   elif split[0] == "float":
      if args.core.upper() == "CVA6":
         targetSW = os.environ.get(targetSW_prefix + "FLOAT")
      else:
         raise RuntimeError(f"Target-SW float is currently not supported for {args.core.upper()}")
   else:
      targetSW_failed = True
elif len(split:=args.targetSW.split(":")) == 2:
   if split[0] == "em":
      targetSW = os.environ.get(targetSW_prefix + "EMBENCH") + "/" + split[1]
   elif split[0] == "dhry":
      targetSW = os.environ.get(targetSW_prefix + "DHRYSTONE_OFFSET") + "-" + split[1]
   elif split[0] == "custom":
      targetSW = split[1]
   else:
      targetSW_failed = True
else:
   targetSW_failed = True
   
if targetSW_failed:
   sys.exit("FATAL: Target-SW handle \"" + args.targetSW + "\" is not supported!")

# Resolve BOOTROM (if applicable)
if args.core == "cva6":
   sim_args += " --bootrom " + os.environ.get(targetSW_prefix + "BOOTROM")

# Parsing power report for average total power report
if args.uArchPowerreport is None:
   sys.exit("FATAL: Called support-script run_etiss_energy_estimate.py without path to commercial power report provided")
if args.uArchTopmodule is None:
   sys.exit("FATAL: Called support-script run_etiss_energy_estimate.py without specifying the top module in power report")

average_power=0
in_hierarchy_part=False
try:
    report = open(args.uArchPowerreport, 'r')
    Lines = report.readlines()
except:
    sys.exit("FATAL: Path to commercial power report is not correct")

for line in Lines:
    elements=line.split()
    if len(elements)<=1:
       continue
    if elements[0]== "Hierarchy":
        in_hierarchy_part=True

    if in_hierarchy_part:
        if elements[0]== args.uArchTopmodule:
            average_power=elements[-2]
            break
    else:
        continue


if (average_power ==0):
   sys.exit("FATAL: Average total power of top module not found in power report")
 

   
# Execute
simulator = os.environ.get("PSW_PERF_SIM")
exe = simulator + "/run_simulator.py " + targetSW + sim_args

exe= exe + " --uArchPower " + str(average_power)

# Adding cycle time for energy estimate
if args.uArchCycletime is None:
   sys.exit("FATAL: Called support-script run_etiss_energy_estimate.py without specifying core's cycle time in ns")
else:
   exe = exe + " --uArchCycletime " + str(args.uArchCycletime)
   
for arg_i in args_passThrough:
   exe += " " + arg_i
   
os.system(exe)
