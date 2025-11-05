import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parents[1] / 'csv_sheets'

files = {
    'alerts': base / 'alerts.csv',
    'resources': base / 'resources.csv',
    'affected_regions': base / 'affected_regions.csv'
}

results = {}

# Load and compute unique sets
alerts_df = pd.read_csv(files['alerts'])
results['alerts_severity'] = sorted(alerts_df['severity'].dropna().astype(str).unique().tolist())

resources_df = pd.read_csv(files['resources'])
results['resources_status'] = sorted(resources_df['status'].dropna().astype(str).unique().tolist())

regions_df = pd.read_csv(files['affected_regions'])
results['affected_regions_risk_level'] = sorted(regions_df['risk_level'].dropna().astype(str).unique().tolist())

print('CSV reference unique values:')
for k, v in results.items():
    print(f"- {k}: {v}")

# Expected dropdowns after update are DB distinct values with CSV fallback
print('\nValidation Notes:')
print('- Alert Center severity dropdown sources DB distinct severities, fallback to CSV severities; should match above set when DB not connected.')
print('- Resource Overview status dropdowns source DB distinct statuses, fallback to CSV; should match above set when DB not connected.')
print('- Database Explorer add forms now use DB distinct values (risk_level/status/severity), fallback to CSV; should match sets above when DB not connected.')
