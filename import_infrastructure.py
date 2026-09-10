# import_infrastructure.py
import csv
from db import query

def import_dataset(csv_path="dataset.csv"):
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            query("""
                INSERT INTO reference_infrastructure (location_id, expected_type, geom)
                VALUES (%s, %s, ST_MakePoint(%s, %s)::geography)
            """, (row["location_id"], row["expected_type"], row["longitude"], row["latitude"]), fetch=False)
            count += 1
    print(f"Imported {count} rows")

if __name__ == "__main__":
    import_dataset()