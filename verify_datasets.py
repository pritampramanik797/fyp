import pandas as pd

print('='*60)
print('FINAL DATASET SUMMARY')
print('='*60)

datasets = {
    'Inverter': 'inverter/inverter_dataset_complete.csv',
    'NOR': 'nor/nor_dataset_complete.csv',
    'NAND': 'nand/nand_dataset_complete.csv'
}

total = 0
for name, path in datasets.items():
    df = pd.read_csv(path)
    size = len(df)
    total += size
    gate_id = df['Gate_ID'].iloc[0] if 'Gate_ID' in df.columns else 'N/A'
    print(f'{name:12} | {size:5} rows | Gate_ID: {gate_id}')

print('-'*60)
print(f'{"TOTAL":12} | {total:5} rows')
print('='*60)
