import time
import json
import os
from datetime import datetime
from tqdm import tqdm



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


data_source_file_path = "exhibitors_data/exhibitors.json"
output_path = os.path.join(os.getcwd(), f"exhibitors_data/exhibitors_detailed_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json")


def scrape_exhibitors_information():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)
    
    with open(data_source_file_path, "r", encoding="utf-8") as f:
        exhibitor_list = json.load(f)
    
    min_counter = 722

    results = []
    for item in tqdm(exhibitor_list[min_counter:1000], desc="Processing", unit="item"):
        link = item.get("link")

        print("--------------------")
        print(link)

        try:
            driver.get(link)
            time.sleep(15)

            WebDriverWait(driver, 30).until(
               lambda d: d.execute_script("return document.readyState") == "complete"
               )
            
            # Company name
            try:
                exibitor_name = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.sc-guNwuy.crpMCq"))
                )
                exibitor_name = exibitor_name.text.strip()
            except:
                exibitor_name = "No name found"

            try:
                exibitor_information = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-faJNnW.ftfZCw"))
                )
                exibitor_information = exibitor_information.text.strip()
            except:
                exibitor_information = "No information found"

            # Company activity
            try:
                exibitor_activities = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-cJIyfF.cvMBHw"))
                )
                exibitor_activities = exibitor_activities.text.strip()
            except:
                exibitor_activities = "No activities found"

            # Company thematic
            try:
                thematic_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='sc-hfAwGc cKDOHH' and text()='Thématique']"
                        "/following-sibling::div[@class='sc-daNmkL fBOHHx']"
                    )
                )
            )
                thematic_section = thematic_section.text.strip()
            except:
                thematic_section = "No thematic found"
            
            # Company country
            try:
                country = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@class='sc-hfAwGc cKDOHH' and text()='Pays']"
                            "/following-sibling::div[@class='sc-daNmkL fBOHHx']"
                        )
                    )
                )
                country = country.text.strip()
            except:
                country = "No country found"

            # Company contacts
            try:
                contact_container = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//h2[normalize-space()='Détails du contact']/ancestor::div[contains(@class, 'sc-djPPSU')]"
                        )
                    )
                )
                contact_rows = contact_container.find_elements(By.CSS_SELECTOR, "div.sc-eNSrOW.dySuYf")
                contact_rows = [contact.text.strip() for contact in contact_rows]

            except:
                contact_container = "No contacts found"

            # Company members
            try:
                member_blocks = driver.find_elements(
                    By.XPATH,
                    "//div[@id='team']/following-sibling::div[contains(@class, 'sc-bJqjYt') and contains(@class, 'hifVOW')]"
                )

                team_members = []
                for block in member_blocks:
                    try:
                        name_el = block.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-dUYLmH.cBbmeX.cjPHDI")
                        name = name_el.text.strip()
                    except:
                        name = "No name found"

                    try:
                        position_el = block.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-cezyBN.cBbmeX.cQkxBs")
                        position = position_el.text.strip()
                    except:
                        position = "No position found"

                    try:
                        company_el = block.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-fUkmAC.cBbmeX.fohyWG")
                        company = company_el.text.strip()
                    except:
                        company = "No company found"
                    
                    team_members.append({
                        "name": name,
                        "position": position,
                        "company": company
                    })
            except:
                team_members = "No member found" 

            # Social medials
            try:
                social_container = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-jGONNV.gMaPYA"))
                )

                social_links = social_container.find_elements(By.TAG_NAME, "a")
                social_links = [link.get_attribute("href") for link in social_links]
            except:
                social_links = "No social links found"

                
            exhibitor_information = {
                    "index": min_counter,
                    "timestamp": datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
                    "exibitor_name": exibitor_name,
                    "exibitor_information": exibitor_information,
                    "exibitor_activities": exibitor_activities,
                    "thematic_section": thematic_section,
                    "contact_rows": contact_rows,
                    "team_members": team_members,
                    "social_links": social_links,
                    "link": link
                }
            results.append(exhibitor_information)
            min_counter += 1
            
            print(exhibitor_information)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)   

        except:
            print("Error occurred")
    
    driver.quit()

if __name__ == "__main__":
    scrape_exhibitors_information()