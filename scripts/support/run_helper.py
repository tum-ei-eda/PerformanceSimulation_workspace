#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

# Read input arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("targetSW", help="Target software handle (e.g.: dhry, em:cubic)")
argParser.add_argument("-c", "--core", help="Target core architecture [cv32e40p | cva6]")
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
   elif Path(args.targetSW).is_file():
      targetSW = args.targetSW
   else:
      targetSW_failed = True
elif len(split:=args.targetSW.split(":")) == 2:
   if split[0] == "em":
      targetSW = os.environ.get(targetSW_prefix + "EMBENCH") + "/" + split[1]
   elif split[0] == "dhry":
      targetSW = os.environ.get(targetSW_prefix + "DHRYSTONE_OFFSET") + "-" + split[1]
   else:
      targetSW_failed = True
else:
   targetSW_failed = True
   
if targetSW_failed:
   sys.exit("FATAL: Target-SW handle \"" + args.targetSW + "\" is not supported!")

# Resolve BOOTROM (if applicable)
if args.core == "cva6":
   sim_args += " --bootrom " + os.environ.get(targetSW_prefix + "BOOTROM")
   
# Execute
simulator = os.environ.get("PSW_PERF_SIM")
exe = simulator + "/run_simulator.py " + targetSW + sim_args
for arg_i in args_passThrough:
   exe += " " + arg_i
   
os.system(exe)
