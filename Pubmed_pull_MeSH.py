import requests
import json
import csv
import os
from xml.etree import ElementTree as ET

# Define the PubMed API endpoints
PUBMED_SEARCH_API_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_API_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_API_KEY = ""  # Replace with your actual PubMed API key


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


def names_to_search(set):
    res = []
    json_file_path = 'matches.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    names_list = data
    for i in range(len(set)):
        if set[i] not in names_list:
            if ',' in set[i]:
                res.append(set[i][:set[i].index(',')])
            else:
                res.append(set[i])

    return res


def main():
    comparison_csv_path = "columbia_research_faculty_extracted.csv"

    # Load the names from the comparison CSV file
    comparison_names = []
    with open(comparison_csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            comparison_names.append(row['Name'])

    names = names_to_search(comparison_names)

    for author_name in names:
        print(f"Pulling articles of {author_name}")
        if author_name == "N/A":
            continue
        # Search PubMed by author name
        search_results = search_pubmed_by_author(author_name)
        pmids = search_results['esearchresult']['idlist']
        print(f"{len(pmids)} articles found")

        if not pmids:
            print(f"No articles found for author: {author_name}")
            print("=======================================================")
            continue

        # Get details for the found PMIDs
        pubmed_data = fetch_pubmed_article_details(pmids)

        # Process the data into the required format
        articles = parse_article_details(pubmed_data)

        # Output the results
        output_dir = 'researchers_files(Yilu_format)'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{author_name}.json')

        with open(output_path, 'w', encoding='utf-8') as output_file:
            json.dump(articles, output_file, indent=4)

        print(f"Data saved to {output_path}")
        print("=======================================================")


if __name__ == "__main__":
    main()
