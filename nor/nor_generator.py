import subprocess
import re
import csv
import os
import random

# --- CONFIGURATION ---
# Updated path as per your instruction
LTSPICE_EXE = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
MASTER_CIR = "nor.cir"
FINAL_DATASET = "nor_gate_dataset_5000.csv"
NUM_POINTS = 5

def get_power_from_log(log_file):
    p_total = 0.0
    p_static = 0.0
    if os.path.exists(log_file):
        # LTspice logs are typically UTF-16
        with open(log_file, 'r', encoding='utf-16', errors='ignore') as f:
            content = f.read()
            # Absolute value used to handle SPICE current direction notation
            avg_match = re.search(r"avg_power:.*?=-(.*?)\s", content)
            stat_match = re.search(r"p_static:.*?=-(.*?)\s", content)
            if avg_match: p_total = abs(float(avg_match.group(1)))
            if stat_match: p_static = abs(float(stat_match.group(1)))
    return p_total, p_static

print(f"Initializing automation in: {os.getcwd()}")

with open(FINAL_DATASET, 'w', newline='') as csvfile:
    fieldnames = ['vdd', 'freq_hz', 'temp', 'slew_ps', 'load_ff', 'p_total', 'p_static']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(NUM_POINTS):
        # 1. Randomize Features
        vdd = round(random.uniform(0.7, 1.3), 3)
        temp = round(random.uniform(-25, 125), 1)
        slew = round(random.uniform(10, 500), 1)
        load = round(random.uniform(1, 100), 1)
        freq = random.uniform(1e8, 2e9) 
        
        period = 1.0 / freq
        p_width = period / 2.0

        # 2. Modify the Netlist
        with open(MASTER_CIR, 'r') as f:
            lines = f.readlines()
        
        with open("temp_run.cir", "w") as f:
            for line in lines:
                if ".param vdd_val" in line: f.write(f".param vdd_val = {vdd}\n")
                elif ".param temp_val" in line: f.write(f".param temp_val = {temp}\n")
                elif ".param slew_val" in line: f.write(f".param slew_val = {slew}p\n")
                elif ".param cap_val" in line: f.write(f".param cap_val = {load}f\n")
                # Update inputs Va and Vb
                elif "Va inA" in line: f.write(f"Va inA 0 PULSE(0 {vdd} 1n {slew}p {slew}p {p_width} {period})\n")
                elif "Vb inB" in line: f.write(f"Vb inB 0 PULSE(0 {vdd} 1.2n {slew}p {slew}p {p_width*0.7} {period*1.4})\n")
                else: f.write(line)

        # 3. Execute LTspice in Batch Mode
        subprocess.run([LTSPICE_EXE, "-b", "-Run", "temp_run.cir"], capture_output=True)

        # 4. Extract and Save
        total_p, static_p = get_power_from_log("temp_run.log")
        writer.writerow({
            'vdd': vdd, 'freq_hz': freq, 'temp': temp, 
            'slew_ps': slew, 'load_ff': load, 
            'p_total': total_p, 'p_static': static_p
        })

        if i % 100 == 0:
            print(f"Completed {i}/{NUM_POINTS} | Current P_total: {total_p:.3e} W")

print(f"\nDone! Dataset ready: {FINAL_DATASET}")