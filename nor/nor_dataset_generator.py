import os
import subprocess
import re
import pandas as pd
import numpy as np
from pathlib import Path

# --- Configuration ---
LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
MODEL_FILE = "45nm_HP.pm"
CIRCUIT_FILE = "nor.cir"
OUTPUT_PREFIX = "nor_dataset"

# Verify files exist
if not Path(MODEL_FILE).exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_FILE}")
if not Path(LTSPICE_PATH).exists():
    raise FileNotFoundError(f"LTspice not found: {LTSPICE_PATH}")

# --- Feature Ranges (Standardized with Inverter) ---
vdd_range = np.arange(0.7, 1.3, 0.1)      # 0.7V to 1.2V
cload_range = np.linspace(1e-15, 50e-15, 12) 
slew_range = [10e-12, 50e-12, 100e-12, 200e-12, 400e-12] 
temp_range = [-40, -25, 0, 25, 75, 100, 125]  
wp_range = [180e-9, 360e-9]               

dataset = []
chunk_counter = 0
chunk_number = 1
total_iterations = len(vdd_range) * len(cload_range) * len(slew_range) * len(temp_range) * len(wp_range)
iteration = 0

print(f"Starting NOR2 Data Factory... ({total_iterations} simulations)")

# --- Simulation Loop ---
for vdd in vdd_range:
    for cl in cload_range:
        for slew in slew_range:
            for temp in temp_range:
                for wp in wp_range:
                    iteration += 1
                    if iteration % 100 == 0:
                        print(f"Progress: {iteration}/{total_iterations}")
                    
                    # Note: Using wn=90n fixed as per your inverter setup
                    # Note: Using 2-input pulse pattern to exercise all states
                    netlist = f"""* Generated NOR2 Netlist
.include {MODEL_FILE}
.param vdd_val={vdd}
.param cload_val={cl}
.param slew_val={slew}
.param temp_val={temp}
.param wn=90n
.param wp={wp}

* Power Supply
Vdd vdd 0 {{vdd_val}}

* Inputs (Offset to test all transitions: 00, 01, 11, 10)
Va a 0 PULSE(0 {{vdd_val}} 0 {{slew_val}} {{slew_val}} 1n 2n)
Vb b 0 PULSE(0 {{vdd_val}} 0 {{slew_val}} {{slew_val}} 2n 4n)

* NOR2 Topology
M1 int a vdd vdd pmos W={{wp}} L=45n
M2 out b int vdd pmos W={{wp}} L=45n
M3 out a 0   0   nmos W={{wn}} L=45n
M4 out b 0   0   nmos W={{wn}} L=45n

CL out 0 {{cload_val}}

.temp {{temp_val}}
.tran 0 8n 0 1p
.measure tran avg_pwr AVG -I(Vdd)*{{vdd_val}} FROM=1n TO=7n
.end
"""
                    with open(CIRCUIT_FILE, "w") as f:
                        f.write(netlist)

                    # Run LTspice in Batch Mode
                    try:
                        subprocess.run([LTSPICE_PATH, "-b", CIRCUIT_FILE], 
                                     capture_output=True, timeout=30, text=True)
                    except Exception as e:
                        print(f"Error at {iteration}: {e}")
                        continue

                    # Parse Log
                    log_file = CIRCUIT_FILE.replace(".cir", ".log")
                    if os.path.exists(log_file):
                        try:
                            with open(log_file, "r") as f:
                                log_content = f.read()
                                match = re.search(r"avg_pwr.*?=\s*([\d\.e\+\-]+)", log_content, re.IGNORECASE)
                                if match:
                                    power = abs(float(match.group(1)))
                                    dataset.append([vdd, cl, slew, temp, wp, power])
                                    chunk_counter += 1
                                    
                                    if chunk_counter == 1000:
                                        chunk_file = f"{OUTPUT_PREFIX}_chunk_{chunk_number}.csv"
                                        pd.DataFrame(dataset, columns=['Vdd', 'Cload', 'Slew', 'Temp', 'Wp', 'Power']).to_csv(chunk_file, index=False)
                                        print(f"  → Saved {chunk_file}")
                                        dataset = []
                                        chunk_counter = 0
                                        chunk_number += 1
                        except Exception as e:
                            print(f"Error parsing log at iteration {iteration}: {e}")
                            continue

                    # Cleanup
                    for ext in [".log", ".raw"]:
                        tmp = CIRCUIT_FILE.replace(".cir", ext)
                        if os.path.exists(tmp): os.remove(tmp)

# Final Save
if dataset:
    pd.DataFrame(dataset, columns=['Vdd', 'Cload', 'Slew', 'Temp', 'Wp', 'Power']).to_csv(f"{OUTPUT_PREFIX}_chunk_{chunk_number}.csv", index=False)

print("\nNOR2 Generation Complete.")