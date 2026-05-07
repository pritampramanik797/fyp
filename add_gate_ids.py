import pandas as pd

print("Adding Gate_ID to inverter and nor datasets...")
print("="*60)

# Add Gate_ID to inverter (Gate_ID = 1 for Inverter)
inv_df = pd.read_csv("inverter/inverter_dataset_complete.csv")
inv_df.insert(5, 'Gate_ID', 1)  # Insert at position 5 (before Power)
inv_df.to_csv("inverter/inverter_dataset_complete.csv", index=False)
print(f"✅ Inverter: Added Gate_ID=1 to {len(inv_df)} rows")
print(f"   Columns: {list(inv_df.columns)}")

# Add Gate_ID to nor (Gate_ID = 3 for NOR)
nor_df = pd.read_csv("nor/nor_dataset_complete.csv")
nor_df.insert(5, 'Gate_ID', 3)  # Insert at position 5 (before Power)
nor_df.to_csv("nor/nor_dataset_complete.csv", index=False)
print(f"✅ NOR: Added Gate_ID=3 to {len(nor_df)} rows")
print(f"   Columns: {list(nor_df.columns)}")

# Verify NAND still has Gate_ID=2
nand_df = pd.read_csv("nand/nand_dataset_complete.csv")
print(f"✅ NAND: Gate_ID=2 for {len(nand_df)} rows")
print(f"   Columns: {list(nand_df.columns)}")

print("\n" + "="*60)
print("Summary:")
print(f"  Inverter: {len(inv_df)} rows | Gate_ID=1")
print(f"  NOR:      {len(nor_df)} rows | Gate_ID=3")
print(f"  NAND:     {len(nand_df)} rows | Gate_ID=2")
print("="*60)
