from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests


# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Open the webpage
def scrape_hidden(link, faculty_data, department):
    driver.get(link)

    # Allow the page to load completely
    time.sleep(3)

    # Find all "Show more" buttons and click them
    show_more_buttons = driver.find_elements(By.CLASS_NAME, "show-hide-controller")

    for button in show_more_buttons:
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)  # Allow time for content to be revealed

    # Allow time for all content to be revealed
    time.sleep(5)

    # Extract content after clicking "Show more"
    content_div = driver.find_element(By.ID, 'cb-content__main')
    html_content = content_div.get_attribute('innerHTML')


    # Close the driver
    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all persons' sections
    person_sections = soup.find_all('div', class_='entity entity-paragraphs-item paragraphs-item-person cb-person')

    for person in person_sections:
        # Extract name
        name_tag = person.find('h4',
                               class_='field field-name-field-person-full-name field-type-text field-label-hidden cb-person__name')
        name = name_tag.get_text(strip=True) if name_tag else 'N/A'

        # Extract position
        position_tag = person.find('ul',
                                   class_='field field-name-field-person-position field-type-text field-label-hidden cb-person__positions')
        position = position_tag.find('li').get_text(strip=True) if position_tag else 'N/A'

        # Extract phone number
        phone_tag = person.find('a', class_='phone-link')
        phone = phone_tag.get_text(strip=True) if phone_tag else 'N/A'

        # Extract email
        email_tag = person.find('a', href=True)
        email = email_tag['href'].replace('mailto:', '') if email_tag and 'mailto:' in email_tag['href'] else 'N/A'

        # Extract biography
        bio_tag = person.find('div',
                              class_='field field-name-field-person-bio field-type-text-long field-label-hidden jquery-once-1-processed show-hide show-hide-processed')
        bio = bio_tag.get_text(strip=True) if bio_tag else 'N/A'
        faculty_data.append({
            "Name": name,
            "Department": department,
            "Research Introduction": bio,
            "Research Interests": "N/A",
            "Selected Publications": "N/A",
            "External Links": "N/A"
        })

def extract_info_from_html(profile_soup):
    # Extract the name
    name_tag = profile_soup.find('h2', style="white-space:pre-wrap;")
    name = name_tag.get_text(strip=True) if name_tag else "N/A"

    # Extract the research introduction
    research_intro = ""
    research_intro_tag = profile_soup.find('strong', string='Research')
    if research_intro_tag:
        next_sibling = research_intro_tag.next_sibling
        while next_sibling:
            if isinstance(next_sibling, Tag):
                research_intro += next_sibling.get_text(separator=' ', strip=True)
            else:
                research_intro += next_sibling.strip()
            next_sibling = next_sibling.next_sibling
            if isinstance(next_sibling, Tag) and next_sibling.name == 'strong':
                break  # Stop if encounter another strong tag, indicating a new section

    research_intro = research_intro.strip() if research_intro else "N/A"

    return name, research_intro

def extract_research_info_physiology_format(full_text, soup):
    # name_element = soup.find('h2', {'class': 'font_2 wixui-rich-text__text'})
    # name = name_element.get_text(strip=True) if name_element else 'Name not found'
    #
    # # Extract the research intro
    # research_intro_element = None
    # for element in soup.find_all('div', {'data-testid': 'richTextElement'}):
    #     if 'Professor of Physiology' in element.get_text():
    #         research_intro_element = element.find('p', {'class': 'font_7 wixui-rich-text__text'})
    #         break
    # research_intro = research_intro_element.get_text(
    #     strip=True) if research_intro_element else 'Research intro not found'
    #
    #
    # # Extract the research interests
    # research_interests = []
    # for p in soup.find_all('p', class_='font_8 wixui-rich-text__text'):
    #     text = p.get_text(strip=True)
    #     if text:  # Skip empty paragraphs
    #         research_interests.append(text)
    # return name,  " ".join(research_interests[1:]), research_intro
    lst = full_text.split('|')
    name = ""
    research_interests = ""
    for i in range(len(lst)):
        if "use tab to navigate" in lst[i].lower():
            name = lst[i+1]
        if "current research" == lst[i].lower():
            research_interests = lst[i-1]
    research_intro = []
    for p in soup.find_all('p', class_='font_8 wixui-rich-text__text'):
        text = p.get_text(strip=True)
        if text:  # Skip empty paragraphs
            research_intro.append(text)
    return name if name != "" else "N/A", research_interests if research_interests != "" else "N/A", " ".join(research_intro[1:]) if len(research_intro) != 0 else "N/A"


def scrape_faculty_info_system_biology(soup):
    # Find the name
    name_tag = soup.find('h1', {'id': 'page-title'})

    name = name_tag.get_text(strip=True)

    # Find the research introduction
    intro_tag = soup.find('div', {'class': 'field--name-field-profile'})
    intro = intro_tag.get_text(strip=True)


    return name, intro
