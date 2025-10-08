from hkjc import generate_historical_data

df = generate_historical_data('2024-09-08', '2025-10-06')
df.write_parquet('2024-2025-hkjc.parquet')