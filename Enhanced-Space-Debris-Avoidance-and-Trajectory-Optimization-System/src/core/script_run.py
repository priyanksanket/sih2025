# debug_csv.py
import os

# Get the project root directory dynamically
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
csv_path = os.path.join(base_dir, "data", "rocket_parameters.csv")

with open(csv_path, 'r') as f:
    print("First 5 lines:")
    for i, line in enumerate(f.readlines()[:5], 1):
        print(f"Line {i}: {line.strip()}")