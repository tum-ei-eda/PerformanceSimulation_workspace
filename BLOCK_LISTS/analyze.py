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

import json
from pathlib import Path
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

def read_file_stats(file_path):
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    blocks = data.get("blocks", [])
    block_count = len(blocks)
    instr_counts = [len(block.get("instrs", [])) for block in blocks]
    max_instrs = max(instr_counts, default=0)
    avg_instrs = sum(instr_counts) / block_count if block_count else 0.0

    return block_count, max_instrs, avg_instrs

def process(core_, long_=False):
    stats = []

    for file_i in file_names:
        if core_ in file_i:
            if ((not long_) and not ("LONG" in file_i)) or (long_ and ("LONG" in file_i)):
                file_path = script_dir / file_i
                block_count, max_instrs, avg_instrs = read_file_stats(file_path)
                stats.append((file_i, block_count, max_instrs, avg_instrs))

    if not stats:
        return

    # build display labels by removing core prefix and suffix, then sort
    entries = []
    suffix = "_BlockList.json"
    prefix = f"{core_}_"
    for file_i, block_count, max_instrs, avg_instrs in stats:
        label = file_i
        if label.startswith(prefix):
            label = label[len(prefix):]
        if label.endswith(suffix):
            label = label[: -len(suffix)]
        entries.append((label, file_i, block_count, max_instrs, avg_instrs))

    # sort entries alphabetically by the display label (case-insensitive)
    entries.sort(key=lambda e: e[0].lower())

    report_path = script_dir / f"{core_}_LONG_analysis.txt" if long_ else script_dir / f"{core_}_analysis.txt"
    with report_path.open("w", encoding="utf-8") as report_file:
        for label, file_i, block_count, max_instrs, avg_instrs in entries:
            report_file.write(
                f"{file_i}: blocks={block_count}, max_instrs={max_instrs}, avg_instrs={avg_instrs:.2f}\n"
            )

    # prepare sorted lists for plotting
    file_labels = [label for label, *_ in entries]
    block_counts = [block_count for *_, block_count, _, _ in entries]
    max_instrs_values = [max_instrs for *_, max_instrs, _ in entries]
    avg_instrs_values = [avg_instrs for *_, avg_instrs in entries]

    if plt is not None:
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 14), constrained_layout=True)
        x_positions = range(len(file_labels))

        axes[0].bar(x_positions, block_counts, color="tab:blue")
        axes[0].set_title(f"{core_} block counts")
        axes[0].set_ylabel("Blocks")

        axes[1].bar(x_positions, max_instrs_values, color="tab:orange")
        axes[1].set_title(f"{core_} maximum instructions per block")
        axes[1].set_ylabel("Max instructions")

        axes[2].bar(x_positions, avg_instrs_values, color="tab:green")
        axes[2].set_title(f"{core_} average instructions per block")
        axes[2].set_ylabel("Avg instructions")
        axes[2].set_xticks(list(x_positions))
        axes[2].set_xticklabels(file_labels, rotation=45, ha="right")

        for ax in axes:
            ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig_path = script_dir / f"{core_}_LONG_analysis.png" if long_ else script_dir / f"{core_}_analysis.png"
        fig.savefig(fig_path)
        plt.close(fig)
    else:
        print(f"matplotlib not available — skipping plot for {core_}. Install matplotlib to enable plotting.")


### MAIN ###

this_script = Path(__file__).resolve()

script_dir = this_script.parent
# only consider JSON files in the directory
file_names = [p.name for p in script_dir.iterdir() if p.is_file() and p.suffix.lower() == ".json"]

cores = ["CV32E40P_DSE", "CVA6_DSE"]

for core_i in cores:
    process(core_i)
    process(core_i, long_=True)

#    stats = []
#
#    for file_i in file_names:
#        if core_i in file_i and not ("LONG" in file_i):
#            file_path = script_dir / file_i
#            block_count, max_instrs, avg_instrs = read_file_stats(file_path)
#            stats.append((file_i, block_count, max_instrs, avg_instrs))
#
#    if not stats:
#        continue
#
#    # build display labels by removing core prefix and suffix, then sort
#    entries = []
#    suffix = "_BlockList.json"
#    prefix = f"{core_i}_"
#    for file_i, block_count, max_instrs, avg_instrs in stats:
#        label = file_i
#        if label.startswith(prefix):
#            label = label[len(prefix):]
#        if label.endswith(suffix):
#            label = label[: -len(suffix)]
#        entries.append((label, file_i, block_count, max_instrs, avg_instrs))
#
#    # sort entries alphabetically by the display label (case-insensitive)
#    entries.sort(key=lambda e: e[0].lower())
#
#    report_path = script_dir / f"{core_i}_analysis.txt"
#    with report_path.open("w", encoding="utf-8") as report_file:
#        for label, file_i, block_count, max_instrs, avg_instrs in entries:
#            report_file.write(
#                f"{file_i}: blocks={block_count}, max_instrs={max_instrs}, avg_instrs={avg_instrs:.2f}\n"
#            )
#
#    # prepare sorted lists for plotting
#    file_labels = [label for label, *_ in entries]
#    block_counts = [block_count for *_, block_count, _, _ in entries]
#    max_instrs_values = [max_instrs for *_, max_instrs, _ in entries]
#    avg_instrs_values = [avg_instrs for *_, avg_instrs in entries]
#
#    if plt is not None:
#        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 14), constrained_layout=True)
#        x_positions = range(len(file_labels))
#
#        axes[0].bar(x_positions, block_counts, color="tab:blue")
#        axes[0].set_title(f"{core_i} block counts")
#        axes[0].set_ylabel("Blocks")
#
#        axes[1].bar(x_positions, max_instrs_values, color="tab:orange")
#        axes[1].set_title(f"{core_i} maximum instructions per block")
#        axes[1].set_ylabel("Max instructions")
#
#        axes[2].bar(x_positions, avg_instrs_values, color="tab:green")
#        axes[2].set_title(f"{core_i} average instructions per block")
#        axes[2].set_ylabel("Avg instructions")
#        axes[2].set_xticks(list(x_positions))
#        axes[2].set_xticklabels(file_labels, rotation=45, ha="right")
#
#        for ax in axes:
#            ax.grid(axis="y", linestyle="--", alpha=0.4)
#
#        fig_path = script_dir / f"{core_i}_analysis.png"
#        fig.savefig(fig_path)
#        plt.close(fig)
#    else:
#        print(f"matplotlib not available — skipping plot for {core_i}. Install matplotlib to enable plotting.")

