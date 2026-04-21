#!/usr/bin/env python3

# 
# Copyright 2024 Chair of EDA, Technical University of Munich
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

import argparse
import pathlib
import shutil
import subprocess
import os

######################################### SUPPORT FUNCTIONS #########################################

def getHeaderFiles(dir_):
    return getFiles((dir_ / "include"), ".h")

def getSrcFiles(dir_):
    return getFiles((dir_ / "src"), ".cpp")

def getFiles(dir_, suffix_):
    files = []
    for file_i in dir_.iterdir():
        if file_i.is_file() and (file_i.suffix == suffix_):
            files.append(file_i)
    return files
        
######################################### MAIN ROUTINE #########################################

## INPUT ARGUMENT PARSING ##

argParser = argparse.ArgumentParser()
argParser.add_argument("sourceDir", help="Path to source directory containing files for deployment")
args = argParser.parse_args()

sourceDir = pathlib.Path(args.sourceDir).resolve()

## GATHER SOURCE FILES ##

modelName = sourceDir.name

backendFiles = {"include":[], "src":[]}
monitorFiles = {"include":[], "src":[]}

for dir_i in (sourceDir / "code").iterdir():
    if dir_i.is_dir():
        if dir_i.name in [f"perf_estimator"]:
            # TODO: This is a quick hack. Solve to deploy multiple variants for one model?
            backendFiles["include"].extend(getHeaderFiles(dir_i / modelName))
            backendFiles["src"].extend(getSrcFiles(dir_i / modelName))
        elif dir_i.name in ["channel", "printer"]:
            backendFiles["include"].extend(getHeaderFiles(dir_i))
            backendFiles["src"].extend(getSrcFiles(dir_i))
        elif dir_i.name in ["monitor"]:
            monitorFiles["include"].extend(getHeaderFiles(dir_i))
            monitorFiles["src"].extend(getSrcFiles(dir_i))


## DEPLOY FILES ##

targetLibScripts = os.environ.get("PSW_SWEVAL_LIB_SCRIPTS")

# Deploy backend files
deploy_backend = targetLibScripts + "/deploy_backend.py"

run_deploy_backend = [deploy_backend, modelName]
run_deploy_backend.extend([str(f) for f in backendFiles["include"]])
run_deploy_backend.extend([str(f) for f in backendFiles["src"]])

subprocess.run(run_deploy_backend, check=True)

# Deploy monitor files
deploy_monitor = targetLibScripts + "/deploy_monitor.py"

run_deploy_monitor = [deploy_monitor, modelName]
run_deploy_monitor.extend([str(f) for f in monitorFiles["include"]])
run_deploy_monitor.extend([str(f) for f in monitorFiles["src"]])

subprocess.run(run_deploy_monitor, check=True)
