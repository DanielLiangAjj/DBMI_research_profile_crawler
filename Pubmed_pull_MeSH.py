import requests
import json
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


def search_pubmed_by_author(author_name):
    params = {
        "db": "pubmed",
        "term": author_name,
        "retmax": 400,
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }
    response = requests.get(PUBMED_SEARCH_API_ENDPOINT, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


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
        response = requests.get(PUBMED_FETCH_API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        all_details.append(response.text)

    return all_details


def parse_article_details(xml_data):
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
def names_to_search(set):
    res = []
    folder_path = 'researchers_files(Yilu_format)'
    name_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            name_list.append(os.path.splitext(filename)[0])
    for i in set:
        if i not in name_list and i != "N/A":
            normalized_name = normalize_name(i)
            dropped_middle_name = drop_middle_name(normalized_name)
            if dropped_middle_name != "":
                res.append([normalized_name,dropped_middle_name])
            else:
                res.append([normalized_name])
    return res



    return res


def main():
    comparison_csv_path = "columbia_research_faculty_extracted.csv"
    non_existing_name = []

    # Load the names from the comparison CSV file
    comparison_names = []
    with open(comparison_csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            comparison_names.append(row['Name'])

    names = names_to_search(comparison_names)

    for name_variants in names:
        print(f"Trying names: {name_variants}")

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

        # Get details for the found PMIDs
        pubmed_data = fetch_pubmed_article_details(pmids)

        # Process the data into the required format
        articles = parse_article_details(pubmed_data)

        # Output the results
        output_dir = 'researchers_files(Yilu_format)'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{name_variants[0]}.json')

        with open(output_path, 'w', encoding='utf-8') as output_file:
            json.dump(articles, output_file, indent=4)

        print(f"Data saved to {output_path}")
        print(f"Failed to search for: {non_existing_name}")
        print("=======================================================")


if __name__ == "__main__":
    main()