import pandas as pd
import requests
from Bio import Entrez
import json
import xml.etree.ElementTree as ET
import os

# Set up Entrez email
Entrez.email = "yl8889@nyu.edu"

researchers_name = [
    "Joseph A. Gogos", "Jacqueline Gottlieb", "Richard S. Mann", "Mimi Shirasu-Hiza",
    "Jane Dodd", "Larry Abbott", "Christoph Kellendonk", "Vincent P. Ferrera", "Robert D. Hawkins",
    "Nikolaus Kriegeskorte", "Henry Colecraft", "Eric A. Schon", "Eric Kandel", "Jonathan A. Javitch",
    "Rui M. Costa", "Wayne Hendrickson", "Stavros Lomvardas", "Steven A. Siegelbaum", "David Sulzer",
    "Laura Landweber"
]


# Function to search PubMed based on researcher names
def search_pubmed(researcher_name):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': f"{researcher_name}[Author]",
        'retmode': 'json',
        'retmax': 15
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data.get('esearchresult', {}).get('idlist', [])


# Function to fetch details of articles
def fetch_details(id_list):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    ids = ",".join(id_list)
    params = {
        'db': 'pubmed',
        'id': ids,
        'retmode': 'xml'
    }
    response = requests.get(base_url, params=params)
    return response.text


# Function to parse XML and extract specific information
def parse_article_details(xml_data):
    root = ET.fromstring(xml_data)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        abstract = article.findtext(".//AbstractText")
        pub_date = article.find(".//PubDate")
        pub_date_text = None
        if pub_date is not None:
            year = pub_date.findtext("Year")
            month = pub_date.findtext("Month")
            day = pub_date.findtext("Day")
            pub_date_text = f"{year}-{month}-{day}" if year and month and day else year
        articles.append({
            'title': title,
            'abstract': abstract,
            'pub_date': pub_date_text
        })
    return articles


# Ensure the directory for individual researcher files exists
os.makedirs('researcher_files', exist_ok=True)

articles_data = []
for name in researchers_name:
    print("Searching", name)
    pubmed_ids = search_pubmed(name)
    if pubmed_ids:
        for attempt in range(10):
            try:
                xml_details = fetch_details(pubmed_ids)
                articles = parse_article_details(xml_details)
                print("Fetched articles count:", len(articles))
                articles_data.append({
                    'researcher': name,
                    'articles': articles
                })

                # Save individual researcher data to a JSON file
                individual_file_path = os.path.join('researcher_files', f'{name.replace(" ", "_")}.json')
                with open(individual_file_path, 'w') as f:
                    json.dump({
                        'researcher': name,
                        'articles': articles
                    }, f)

                break  # Exit the retry loop if successful
            except Exception as e:
                print(f"Error fetching details on attempt {attempt + 1}: {e}")
                if attempt == 9:
                    print(f"Failed to fetch details for {name} after 10 attempts")
            except len(articles) == 0:
                print(f"Failed when fetching details on attempt {attempt + 1}: {e}")
                if attempt == 9:
                    print(f"Failed to fetch details for {name} after 10 attempts")
    print("=====================================")

# Save the sampled researchers' names to a separate JSON file
sampled_researchers_file_path = 'sampled_researchers.json'
with open(sampled_researchers_file_path, 'w') as f:
    json.dump(researchers_name, f)

# Save the articles data to a JSON file
articles_data_file_path = 'researcher_articles.json'
with open(articles_data_file_path, 'w') as f:
    json.dump(articles_data, f)

print(f"Sampled researchers saved to {sampled_researchers_file_path}")
print(f"Articles data saved to {articles_data_file_path}")
print(f"Individual researcher files saved in 'researcher_files' directory")
