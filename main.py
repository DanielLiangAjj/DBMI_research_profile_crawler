import requests
from bs4 import BeautifulSoup
import pandas as pd


# Find all the "View Full Profile" links
def get_profile_url(soup):
    profile_links = soup.find_all('a', string='View Full Profile')
    profile_urls = [link['href'] for link in profile_links]

faculty_data = []

# Domains to exclude from external links
excluded_domains = [
    "https://www.cuimc.columbia.edu/",
    "https://www.cuimc.columbia.edu",
    "https://www.nyp.org",
    "https://www.columbiadoctors.org/",
    "https://www.columbia.edu",
    "https://www.cuimc.columbia.edu/privacy-policy",
    "https://www.cuimc.columbia.edu/terms-and-conditions-use",
    "https://www.hipaa.cumc.columbia.edu",
    "facebook.com",
    "twitter.com",
    "youtube.com"
]


# Function to check if a URL is excluded
def is_excluded(url):
    return any(domain in url for domain in excluded_domains)

def get_profile_urls(soup):
    profile_links = soup.find_all('a', string='View Full Profile')
    return [link['href'] for link in profile_links]

def scrape_profile(profile_url, department):
    try:
        profile_response = requests.get(profile_url)
        profile_response.raise_for_status()
        profile_soup = BeautifulSoup(profile_response.content, "html.parser")

        # Extract name
        name = profile_soup.find('h1').get_text(strip=True) if profile_soup.find('h1') else "N/A"

        # Extract Research Introduction
        research_intro_tag = profile_soup.find('div', class_="panel-pane pane-entity-field pane-node-field-cups-research-overview")
        research_intro = research_intro_tag.get_text(strip=True) if research_intro_tag else "N/A"

        # Handle special cases for Research Introduction
        if research_intro == "N/A":
            research_intro_tag = profile_soup.find('div', class_="field-name-field-cups-research-grants")
            if research_intro_tag:
                research_intro = research_intro_tag.get_text(separator=' ', strip=True)

        # Extract entire text content
        full_text = profile_soup.get_text(separator=' ', strip=True)

        # Extract Research Interests, Selected Publications from the full text
        research_interests_start = full_text.find("Research Interests") if "Research Interests" in full_text else -1
        research_interests_end = full_text.find(
            "Selected Publications") if "Selected Publications" in full_text else len(full_text)
        selected_publications_start = full_text.find(
            "Selected Publications") if "Selected Publications" in full_text else -1

        research_interests = full_text[
                             research_interests_start+len("research interests "):research_interests_end].strip() if research_interests_start != -1 else "N/A"
        selected_publications = full_text[
                                selected_publications_start+len("selected publications "):].strip() if selected_publications_start != -1 else "N/A"

        # Extract external links excluding specific domains
        external_links = [a['href'] for a in profile_soup.find_all('a', href=True) if
                          a['href'].startswith('http') and not is_excluded(a['href'])]

        faculty_data.append({
            "Name": name,
            "Department": department,
            "Research Introduction": research_intro,
            "Research Interests": research_interests,
            "Selected Publications": selected_publications,
            "External Links": ", ".join(external_links)
        })

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {profile_url}: {e}")

# List of main webpage URLs to process
main_urls = [
    ("https://www.biochem.cuimc.columbia.edu/research/research-faculty", "Biochemistry and Molecular Biophysics"),
    ("https://www.genetics.cuimc.columbia.edu/about-us/our-faculty", "Genetics and Development"),
    ("https://www.mhe.cuimc.columbia.edu/about-us/leadership-faculty-and-staff", "Medical Humanities and Ethics"),
    ("https://microbiology.columbia.edu/faculty", "Microbiology and Immunology"),
    ("https://www.pharmacology.cuimc.columbia.edu/about-us/our-faculty","Molecular Pharmacology and Therapeutics"),
    ("https://www.vagelos.columbia.edu/departments-centers/neuroscience/our-faculty","Neuroscience"),
    ("https://www.columbiaphysiology.com/faculty","Physiology and Cellular Biophysics"),
    ("https://systemsbiology.columbia.edu/faculty","Systems Biology")
]
for base_url in main_urls:
    next_page_url = base_url[0]
    department = base_url[1]
    print("Scraping", department)
    while next_page_url:
        response = requests.get(next_page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Get profile URLs from the current page
        profile_urls = get_profile_urls(soup)

        # Scrape each profile
        for profile_url in profile_urls:
            scrape_profile(profile_url, department)

        # Find the link to the next page
        next_page_tag = soup.find('li', class_='pager-next')
        if next_page_tag:
            next_page_url = "https://www.biochem.cuimc.columbia.edu" + next_page_tag.find('a')['href']
        else:
            next_page_url = None
# Convert to DataFrame
df = pd.DataFrame(faculty_data)

# Display the DataFrame
print(df)

# Save to a CSV file
df.to_csv("columbia_research_faculty_extracted.csv", index=False)
