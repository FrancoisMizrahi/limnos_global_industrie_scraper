import time
import json
import os
from datetime import datetime


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


data_source_file_path = "exhibitors_data/exhibitors.json"


def scrape_exhibitors_information():
    # 1) Start Selenium (Chrome in this example)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    
    with open(data_source_file_path, "r", encoding="utf-8") as f:
        exhibitor_list = json.load(f)
    
    results = []
    for item in exhibitor_list[:3]:
        link = item.get("link")
        # exibitor_activities = driver.find_element(By.CSS_SELECTOR, "div.sc-cJIyfF.cvMBHw")

        try:
            driver.get(link)
            time.sleep(20)

            WebDriverWait(driver, 30).until(
               lambda d: d.execute_script("return document.readyState") == "complete"
               )

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


            try:
                exibitor_activities = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-cJIyfF.cvMBHw"))
                )
                exibitor_activities = exibitor_activities.text.strip()
            except:
                exibitor_activities = "No activities found"

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


            try:
                contact_container = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//h2[normalize-space()='Détails du contact']/ancestor::div[contains(@class, 'sc-djPPSU')]"
                        )
                    )
                )

                # 4. Within that container, find each row of contact data
                contact_rows = contact_container.find_elements(By.CSS_SELECTOR, "div.sc-eNSrOW.dySuYf")
                contact_rows = [contact.text.strip() for contact in contact_rows]

            except:
                contact_container = "No contacts found"


            print(f"############################")
            print(exibitor_name)
            print(contact_rows)

            results.append({
                    "exibitor_name": exibitor_name,
                    "exibitor_information": exibitor_information,
                    "exibitor_activities": exibitor_activities,
                    "thematic_section": thematic_section,
                    "contact_rows": contact_rows
                })        
        except:
            pass
    
    driver.quit()
    
    # 6) Write everything to a JSON file in the same directory as this script
    output_path = os.path.join(os.getcwd(), f"exhibitors_data/exhibitors_detailed_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(results)} entries to {output_path}")

if __name__ == "__main__":
    scrape_exhibitors_information()