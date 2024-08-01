import os
import json
import csv
import re

# Path to the folder containing the researcher JSON files
folder_path = 'output'
# Path to the CSV file containing the names to compare
comparison_csv_path = "columbia_research_faculty_extracted.csv"

# Load the names from the comparison CSV file
comparison_names = set()
with open(comparison_csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        comparison_names.add(row['Name'])

# Function to extract the name from the filename and convert to "First Last" format
def extract_name_from_filename(filename):
    name, _ = os.path.splitext(filename)  # Remove file extension
    name = name.replace('_', ' ')  # Replace underscores with spaces
    # Split into last and first name
    if ',' in name:
        last_name, first_name = name.split(',', 1)
        name = f"{first_name.strip()} {last_name.strip()}"
    return name

# Function to normalize names by removing titles and converting to a consistent format
def normalize_name(name):
    # Remove titles like "PhD", "MD", etc.
    name = re.sub(r',?\s*(PhD|MD|Dr|Prof)\.?', '', name, flags=re.IGNORECASE)
    # Remove middle names/initials
    name = re.sub(r'\b[A-Z]\.\b', '', name)
    # Remove extra whitespace and convert to lower case
    name = re.sub(r'\s+', ' ', name).strip().lower()
    return name

# Function to check if there are any matches with flexible name matching
def find_matches(file_names, comparison_names):
    normalized_comparison_names = {normalize_name(name) for name in comparison_names}
    matches = set()
    for file_name in file_names:
        normalized_file_name = normalize_name(file_name)
        for comp_name in normalized_comparison_names:
            if normalized_file_name in comp_name or comp_name in normalized_file_name:
                matches.add(file_name)
                break
    return matches

# Traverse the folder and compare names
file_names = set()
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        name = extract_name_from_filename(filename)
        file_names.add(name)

matches = find_matches(file_names, comparison_names)

# Print out the matches
for match in matches:
    print(f"Match found: {match}")

# Save matches to a new JSON file
output_path = 'matches.json'
with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(list(matches), output_file, indent=4)

print(f"Matches saved to {output_path}")
