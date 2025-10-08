from hkjc import generate_historical_data

df = generate_historical_data('2025-10-04', '2025-10-06')
df.write_parquet('hkjc2425.parquet')