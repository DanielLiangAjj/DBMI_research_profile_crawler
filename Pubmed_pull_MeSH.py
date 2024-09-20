from urllib.error import HTTPError

import requests
import json
import time
import csv
from dotenv import load_dotenv
import os
import re
from xml.etree import ElementTree as ET

# Define the PubMed API endpoints
PUBMED_SEARCH_API_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_API_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
load_dotenv()
PUBMED_API_KEY = os.getenv("PubMed_API_KEY")

import os
import json

def check_and_repull_if_empty(output_dir, name_variants):
    # Define the file path
    output_path = os.path.join(output_dir, f'{name_variants[0]}.json')

    # Check if the file exists and is empty (i.e., contains [])
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            if data == []:  # If the file contains an empty list
                print(f"File {output_path} is empty, repulling data for {name_variants[0]}...")
                success = repull_data(output_path, name_variants)
                return success
            else:
                print(f"File {output_path} is not empty, skipping repull for {name_variants[0]}.")
                return True
    else:
        print(f"File {output_path} does not exist, pulling data for the first time.")
        success = repull_data(output_path, name_variants)
        return success


def repull_data(output_path, name_variants):
    # Repull data from PubMed
    pmids = []
    for author_name in name_variants:
        print(f"Searching articles for {author_name}")
        search_results = search_pubmed_by_author(author_name)
        pmids = search_results['esearchresult']['idlist']

        if pmids:
            print(f"{len(pmids)} articles found for {author_name}")
            break  # Exit the loop if we found any articles

    if not pmids:
        print(f"No articles found for any variants of name: {name_variants}")
        return False  # Return False if no data is found

    # Get details for the found PMIDs with error handling
    all_details = fetch_pubmed_article_details(pmids)

    # Process the data into the required format
    articles = parse_article_details(all_details, name_variants)

    # Save the new articles to the output path (overwrite the empty file)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(articles, output_file, indent=4)

    print(f"Data repulled and saved to {output_path}")
    return True  # Return True indicating success


def search_pubmed_by_author(author_name, max_retries=5):
    params = {
        "db": "pubmed",
        "term": author_name,
        "retmax": 400,
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(PUBMED_SEARCH_API_ENDPOINT, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 2))  # Wait time in seconds
                print(f"Rate limit hit for author '{author_name}'. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise e  # Re-raise for other HTTP errors
    else:
        raise HTTPError(f"Failed to fetch after {max_retries} attempts. Status code: {response.status_code}")


def fetch_pubmed_article_details(pmids):
    chunk_size = 200  # Number of PMIDs per request
    all_details = []

    for i in range(0, len(pmids), chunk_size):
        chunk = pmids[i:i + chunk_size]
        params = {
            "db": "pubmed",
            "id": ",".join(chunk),
            "retmode": "xml",
            "api_key": PUBMED_API_KEY
        }

        # Retry logic for handling HTTP 429 errors
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.get(PUBMED_FETCH_API_ENDPOINT, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                all_details.append(response.text)
                break  # Exit retry loop on success
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2))  # Wait time in seconds
                    print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    raise e  # Re-raise for other HTTP errors
        else:
            raise HTTPError(f"Failed to fetch after {max_retries} attempts. Status code: {response.status_code}")

    return all_details

def parse_article_details(xml_data, author_name_variants):
    articles = []
    for chunk in xml_data:
        root = ET.fromstring(chunk)
        for article in root.findall('.//PubmedArticle'):
            pmid = article.findtext('.//PMID')
            title = article.findtext('.//ArticleTitle')
            abstract = article.findtext('.//AbstractText')
            keywords = [kw.text for kw in article.findall('.//Keyword')]
            mesh_terms = [mh.findtext('.//DescriptorName') for mh in article.findall('.//MeshHeading')]

            authors_list = []
            for author in article.findall('.//Author'):
                last_name = author.findtext('.//LastName', '')
                first_name = author.findtext('.//ForeName', '')
                affiliation = author.findtext('.//AffiliationInfo/Affiliation', '')
                authors_list.append({
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Affiliation": affiliation
                })
            if authors_list:
                normalized_author_list = [f"{author['First Name']} {author['Last Name']}".lower().strip() for author in
                                          authors_list]
                author_in_top_3 = any(
                    any(variant in normalized_author_list[i] for variant in author_name_variants)
                    for i in range(min(3, len(authors_list)))  # Top 3 authors
                )
                author_in_senior_position = any(
                    variant in normalized_author_list[-1]
                    for variant in author_name_variants
                )
                if author_in_top_3 or author_in_senior_position:
                    journal = article.findtext('.//Journal/Title')
                    pub_date = article.findtext('.//PubDate/Year')
                    print(f"{len(mesh_terms)} found")
                    articles.append({
                        "PMID": pmid,
                        "Title": title,
                        "Abstract": abstract,
                        "Keywords": keywords,
                        "MeSH terms": mesh_terms,
                        "Authors": authors_list,
                        "Journal": journal,
                        "PubDate": pub_date
                    })

    return articles

def normalize_name(name):
    if "," in name:
        comma_index = name.find(",")
        return name[:comma_index]
    return name

def drop_middle_name(name):
    if "." in name and name[-1] != '.' and name[name.index('.')-2] == " " and name[name.index('.')+1] == ' ':
        res = name[:name.index('.')-1] + name[name.index('.')+2:]
        return res
    else:
        return ""

def names_to_search(name_set):
    print(name_set)
    res = []
    folder_path = 'researchers_files_new'
    name_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            name_list.append(os.path.splitext(filename)[0])
    for name in name_set:
        if name not in name_list and name != "N/A":
            normalized_name = normalize_name(name)
            dropped_middle_name = drop_middle_name(normalized_name)
            if dropped_middle_name != "":
                res.append([normalized_name, dropped_middle_name])
            else:
                res.append([normalized_name])
    return res


def main():
    comparison_csv_path = "columbia_research_faculty_extracted.csv"
    non_existing_name = []
    comparison_json_path = "results_scraper_ed.json"

    # Load the names from the comparison CSV file
    comparison_names = []
    with open(comparison_csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            comparison_names.append(row['Name'])
    # with open(comparison_json_path, 'r') as scraper_file:
    #     scraper_data = json.load(scraper_file)
    #     comparison_names = list(scraper_data.keys())
    target_lst = ["Chunhua Weng", "Gamze Gürsoy", "Sarah Collins Rossetti", "George Hripcsak", "Patrick Ryan", "Krzysztof Kiryluk",
                  "Karen Marder", "Henry Ginsberg", "Ian Kronish", "Samuel Sternberg", "Hashim M. Al-Hashimi", "Shuang Wang",
                  "Zhezhen Jin", "Ying Wei", "Yuanjia Wang", "Soojin Park", "Yiming Luo", "Cong Liu", "Elizabeth Cohn"]
    for i in range(len(target_lst)):
        target_lst[i] = target_lst[i].lower()
    for name in comparison_names:
        if name in target_lst:
            print(name)
            capitalized_name = ""
            for i in range(len(name)):
                if i != 0 and name[i - 1] == " ":
                    capitalized_name += name[i].upper()
                elif i == 0:
                    capitalized_name += name[i].upper()
                else:
                    capitalized_name += name[i]
            comparison_names.append(capitalized_name)

    names = names_to_search(comparison_names)
    print(names)
    output_dir = 'researchers_files_new'
    os.makedirs(output_dir, exist_ok=True)
    for name_variants in names:
        print(f"Trying names: {name_variants}")
        success = check_and_repull_if_empty(output_dir, name_variants)
        if not success:
            non_existing_name.append(name_variants)
        print(f"Failed to search for: {non_existing_name}")
        print("=======================================================")
        pmids = []
        for author_name in name_variants:
            print(f"Searching articles for {author_name}")
            # Search PubMed by author name
            search_results = search_pubmed_by_author(author_name)
            pmids = search_results['esearchresult']['idlist']

            if pmids:
                print(f"{len(pmids)} articles found for {author_name}")
                break  # Exit the loop if we found any articles

        if not pmids:
            print(f"No articles found for any variants of name: {name_variants}")
            non_existing_name.append(name_variants)
            print("=======================================================")
            continue

        # Get details for the found PMIDs with error handling
        chunk_size = 200  # Number of PMIDs per request
        all_details = []

        for i in range(0, len(pmids), chunk_size):
            chunk = pmids[i:i + chunk_size]
            params = {
                "db": "pubmed",
                "id": ",".join(chunk),
                "retmode": "xml",
                "api_key": PUBMED_API_KEY
            }

            # Retry logic for handling HTTP 429 errors
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    response = requests.get(PUBMED_FETCH_API_ENDPOINT, params=params)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    all_details.append(response.text)
                    break  # Exit retry loop on success
                except requests.exceptions.HTTPError as e:
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 2))  # Wait time in seconds
                        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                        time.sleep(retry_after)
                    else:
                        raise e  # Re-raise for other HTTP errors
            else:
                raise HTTPError(f"Failed to fetch after {max_retries} attempts. Status code: {response.status_code}")

        # Process the data into the required format
        articles = parse_article_details(all_details, name_variants)

        # Output the results
        output_dir = 'researchers_files_new'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{name_variants[0]}.json')

        with open(output_path, 'w', encoding='utf-8') as output_file:
            json.dump(articles, output_file, indent=4)
        print(len(articles))
        print(f"Data saved to {output_path}")
        print(f"Failed to search for: {non_existing_name}")
        print("=======================================================")


if __name__ == "__main__":
    main()
