import pandas as pd
import glob

print("Merging NOR dataset...")
print("="*60)

# Load all chunks
files = sorted(glob.glob("nor_dataset_chunk_*.csv"))
print(f"Found {len(files)} chunks\n")

data = []
for f in files:
    df = pd.read_csv(f)
    data.append(df)
    print(f"  {f}: {len(df)} rows")

# Combine
all_data = pd.concat(data, ignore_index=True)
print(f"\n✅ Total: {len(all_data)} rows")

# Save
all_data.to_csv("nor_dataset_complete.csv", index=False)
print(f"💾 Saved: nor_dataset_complete.csv")
print("="*60)
