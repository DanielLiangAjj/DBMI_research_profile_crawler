import os
import json

# Specify the directory containing the JSON files you want to check
directory_to_check = 'researchers_files_new'  # Replace with your directory path

# Iterate over all files in the directory
for filename in os.listdir(directory_to_check):
    if filename.endswith('.json'):
        filepath = os.path.join(directory_to_check, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list) and not data:
                    print(f"File '{filename}' contains an empty list.")
            except json.JSONDecodeError:
                print(f"File '{filename}' is not a valid JSON file.")
