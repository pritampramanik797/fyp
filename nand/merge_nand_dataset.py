import pandas as pd
import glob
import os

print("Merging NAND2 dataset from original and retry runs...")
print("="*60)

# Load all original chunks
original_files = sorted(glob.glob("nand_dataset_chunk_*.csv"))
print(f"\nOriginal chunks found: {len(original_files)}")
original_data = []
for f in original_files:
    df = pd.read_csv(f)
    original_data.append(df)
    print(f"  {f}: {len(df)} rows")

# Load retry successful data
retry_df = pd.read_csv("nand_retry_successful.csv")
print(f"\nRetry successful: {len(retry_df)} rows")

# Combine all
all_data = pd.concat(original_data + [retry_df], ignore_index=True)
print(f"\n✅ Total combined dataset: {len(all_data)} rows")

# Save comprehensive dataset
all_data.to_csv("nand_dataset_complete.csv", index=False)
print(f"\n💾 Saved: nand_dataset_complete.csv")

# Also save chunks for organization
chunk_size = 1000
for i in range(0, len(all_data), chunk_size):
    chunk_num = (i // chunk_size) + 1
    chunk_data = all_data.iloc[i:i+chunk_size]
    chunk_file = f"nand_dataset_final_chunk_{chunk_num}.csv"
    chunk_data.to_csv(chunk_file, index=False)
    print(f"💾 Saved: {chunk_file} ({len(chunk_data)} rows)")

print("\n" + "="*60)
print("Summary:")
print(f"  Total samples: {len(all_data)}")
print(f"  Features: {', '.join(all_data.columns.tolist())}")
print(f"  All NAND gates (Gate_ID=2): {(all_data['Gate_ID'] == 2).sum()}")
print("="*60)
