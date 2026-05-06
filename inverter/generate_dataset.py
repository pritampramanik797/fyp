import os
import subprocess
import re
import pandas as pd
import numpy as np
from pathlib import Path

# --- Configuration ---
LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
MODEL_FILE = "45nm_HP.pm"
CIRCUIT_FILE = "inverter_2.cir"
OUTPUT_CSV = "inverter_dataset_5000.csv"

# Verify files exist
if not Path(MODEL_FILE).exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_FILE}")
if not Path(LTSPICE_PATH).exists():
    raise FileNotFoundError(f"LTspice not found: {LTSPICE_PATH}")

# --- Feature Ranges (Exactly 5,040 combinations) ---
vdd_range = np.arange(0.7, 1.3, 0.1)      # 6 steps (0.7V to 1.2V)
cload_range = np.linspace(1e-15, 50e-15, 12) # 12 steps (1fF to 50fF)
slew_range = [10e-12, 50e-12, 100e-12, 200e-12, 400e-12] # 5 steps
temp_range = [-40, -25, 0, 25, 75, 100, 125]  # 7 steps (expanded)
wp_range = [180e-9, 360e-9]               # 2 steps
# Total: 6 * 12 * 5 * 7 * 2 = 5,040 combinations

dataset = []
chunk_counter = 0
chunk_number = 1
total_iterations = len(vdd_range) * len(cload_range) * len(slew_range) * len(temp_range) * len(wp_range)
iteration = 0

print(f"Starting Data Factory... ({total_iterations} simulations across 6 chunks of ~840 each)")

# --- Simulation Loop ---
for vdd in vdd_range:
    for cl in cload_range:
        for slew in slew_range:
            for temp in temp_range:
                for wp in wp_range:
                    iteration += 1
                    if iteration % 100 == 0:
                        print(f"Progress: {iteration}/{total_iterations}")
                    
                    # Write temporary .cir file
                    netlist = f"""* Generated Inverter Netlist
.include {MODEL_FILE}
.param vdd_val={vdd}
.param cload_val={cl}
.param slew_val={slew}
.param temp_val={temp}
.param wn=90n
.param wp={wp}
M1 out in vdd vdd pmos W={{wp}} L=45n
M2 out in 0 0 nmos W={{wn}} L=45n
CL out 0 {{cload_val}}
Vdd vdd 0 {{vdd_val}}
Vin in 0 PULSE(0 {{vdd_val}} 0 {{slew_val}} {{slew_val}} 1n 2n)
.temp {{temp_val}}
.tran 0 4n 0 1p
.measure tran avg_pwr AVG I(Vdd)*V(vdd) FROM=1n TO=3n
.end
"""
                    with open(CIRCUIT_FILE, "w") as f:
                        f.write(netlist)

                    # Run LTspice
                    try:
                        result = subprocess.run([LTSPICE_PATH, "-b", CIRCUIT_FILE], 
                                              capture_output=True, timeout=30, text=True)
                    except subprocess.TimeoutExpired:
                        print(f"Simulation timeout at iteration {iteration}")
                        continue
                    except Exception as e:
                        print(f"Simulation error at iteration {iteration}: {e}")
                        continue

                    # Parse log file
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
                                    
                                    # Save chunk when it reaches 1000 rows
                                    if chunk_counter == 1000:
                                        chunk_file = f"inverter_dataset_chunk_{chunk_number}.csv"
                                        df = pd.DataFrame(dataset, columns=['Vdd', 'Cload', 'Slew', 'Temp', 'Wp', 'Power'])
                                        df.to_csv(chunk_file, index=False)
                                        print(f"  → Saved {chunk_file} with 1000 rows")
                                        dataset = []
                                        chunk_counter = 0
                                        chunk_number += 1
                        except Exception as e:
                            print(f"Parse error at iteration {iteration}: {e}")
                    
                    # Cleanup
                    for ext in [".log", ".raw"]:
                        temp_file = CIRCUIT_FILE.replace(".cir", ext)
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

# --- Save remaining data (if any) ---
if len(dataset) > 0:
    chunk_file = f"inverter_dataset_chunk_{chunk_number}.csv"
    df = pd.DataFrame(dataset, columns=['Vdd', 'Cload', 'Slew', 'Temp', 'Wp', 'Power'])
    df.to_csv(chunk_file, index=False)
    print(f"  → Saved {chunk_file} with {len(dataset)} rows")

print(f"\nComplete! Generated {chunk_number} CSV files totaling ~{iteration} simulations")
print(f"Files: inverter_dataset_chunk_1.csv through inverter_dataset_chunk_{chunk_number}.csv")