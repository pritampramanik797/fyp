import pandas as pd

print("Updating Gate_ID values...")
print("="*60)

# Update Inverter: Gate_ID = 0
inv_df = pd.read_csv("d:/fyp/final_datasets/inverter_dataset_complete.csv")
inv_df['Gate_ID'] = 0
inv_df.to_csv("d:/fyp/final_datasets/inverter_dataset_complete.csv", index=False)
print(f"✅ Inverter: Gate_ID updated to 0 ({len(inv_df)} rows)")

# Update NAND: Gate_ID = 1
nand_df = pd.read_csv("d:/fyp/final_datasets/nand_dataset_complete.csv")
nand_df['Gate_ID'] = 1
nand_df.to_csv("d:/fyp/final_datasets/nand_dataset_complete.csv", index=False)
print(f"✅ NAND: Gate_ID updated to 1 ({len(nand_df)} rows)")

# Update NOR: Gate_ID = 2
nor_df = pd.read_csv("d:/fyp/final_datasets/nor_dataset_complete.csv")
nor_df['Gate_ID'] = 2
nor_df.to_csv("d:/fyp/final_datasets/nor_dataset_complete.csv", index=False)
print(f"✅ NOR: Gate_ID updated to 2 ({len(nor_df)} rows)")

print("\n" + "="*60)
print("Summary:")
print(f"  Inverter (Gate_ID=0): {len(inv_df)} rows")
print(f"  NAND (Gate_ID=1):     {len(nand_df)} rows")
print(f"  NOR (Gate_ID=2):      {len(nor_df)} rows")
print(f"  Total:                {len(inv_df) + len(nand_df) + len(nor_df)} rows")
print("="*60)
