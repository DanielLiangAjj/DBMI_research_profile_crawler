from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

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

