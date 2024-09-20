import os
import json
import re
import unicodedata  # Import unicodedata for Unicode normalization

def normalize_name(name):
    # Normalize Unicode characters to NFKD form
    name = unicodedata.normalize('NFKD', name)
    # Encode to ASCII bytes, ignore errors (this will remove accents)
    name = name.encode('ascii', 'ignore').decode('ascii')
    # Remove periods, commas, hyphens, underscores, and convert to lowercase
    name = name.lower()
    name = re.sub(r'[.,\-]', ' ', name)
    name_parts = name.strip().split()
    return name_parts

def names_match(name1_parts, name2_parts, match_type='both'):
    # Compare names based on match_type
    if not name1_parts or not name2_parts:
        return False
    if match_type == 'both':
        first_name_match = name1_parts[0] == name2_parts[0]
        last_name_match = name1_parts[-1] == name2_parts[-1]
        return first_name_match and last_name_match
    elif match_type == 'first_name':
        # Only compare first names
        return name1_parts[0] == name2_parts[0]
    elif match_type == 'last_name':
        # Only compare last names
        return name1_parts[-1] == name2_parts[-1]
    else:
        return False

input_dir = 'researchers_files(Yilu_format)'
output_dir = 'researchers_files_new'

json_file = ['Concepcion CP', 'René Hen', 'Emmanuelle Passegué', 'Arthur G Palmer 3rd', 'Daniel Salzman']
match_types = ['last_name', 'last_name', 'first_name', 'last_name', 'last_name']
name_parts = ['Concepcion', 'Hen', 'Emmanuelle', 'Palmer', 'Salzman']

# Create a mapping from json_file to (match_type, name_part)
file_name_mapping = dict(zip(json_file, zip(match_types, name_parts)))

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(input_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract researcher name from filename
        base_filename = os.path.splitext(filename)[0]  # Remove .json extension
        base_filename = base_filename.replace('_', ' ')  # Replace underscores with spaces
        base_filename_normalized = unicodedata.normalize('NFKD', base_filename).encode('ascii', 'ignore').decode('ascii')

        # Determine match_type and researcher_name_parts
        if base_filename in file_name_mapping:
            match_type, name_part = file_name_mapping[base_filename]
            researcher_name_parts = normalize_name(name_part)
        elif base_filename_normalized in file_name_mapping:
            # Handle cases where filename normalization changes the name
            match_type, name_part = file_name_mapping[base_filename_normalized]
            researcher_name_parts = normalize_name(name_part)
        else:
            # Use both first and last names for matching
            match_type = 'both'
            researcher_name_parts = normalize_name(base_filename)

        if not researcher_name_parts:
            # Skip if we can't extract name parts
            continue

        # Now process the articles
        filtered_articles = []
        for article in data:
            authors = article.get('Authors', [])
            # Check if researcher is among top 3 authors or last author
            is_researcher_in_top3 = False
            is_researcher_last_author = False
            for idx, author in enumerate(authors):
                author_first_name = author.get('First Name', '').strip()
                author_last_name = author.get('Last Name', '').strip()
                author_full_name = f"{author_first_name} {author_last_name}"
                author_name_parts = normalize_name(author_full_name)
                if names_match(researcher_name_parts, author_name_parts, match_type=match_type):
                    if idx < 3:
                        is_researcher_in_top3 = True
                    if idx == len(authors) - 1:
                        is_researcher_last_author = True
                    break  # Found researcher in authors
            if is_researcher_in_top3 or is_researcher_last_author:
                filtered_articles.append(article)

        # Write filtered articles to output directory
        output_filepath = os.path.join(output_dir, filename)
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(filtered_articles, f, ensure_ascii=False, indent=4)
