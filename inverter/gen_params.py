import random

# Number of training samples
N = 5000 

# Define realistic 180nm CMOS ranges
ranges = {
    "supply": (0.8, 1.8),       # VDD in Volts
    "cap": (5e-15, 200e-15),    # Load capacitance in Farads (5fF to 200fF)
    "freq": (50e6, 500e6),      # Frequency in Hz (50MHz to 500MHz)
    "slew": (20e-12, 400e-12)   # Input Rise/Fall time in Seconds (20ps to 400ps)
}

def write_spice_table(name, v_min, v_max):
    # Generates: .param name = table(run, 0, val0, 1, val1, ...)
    entries = [f"{i}, {random.uniform(v_min, v_max)}" for i in range(N)]
    return f".param {name} = table(run, {', '.join(entries)})\n"

with open("params.inc", "w") as f:
    f.write("* Automatically generated parameter file for ML training\n")
    for name, (vmin, vmax) in ranges.items():
        f.write(write_spice_table(name, vmin, vmax))

print(f"Successfully generated params.inc with {N} samples.")