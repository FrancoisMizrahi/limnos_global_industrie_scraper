import time
import json
import os
from datetime import datetime


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_exhibitors():
    driver = webdriver.Chrome()

    try:
        url = "https://www.global-industrie.com/liste-des-exposants"
        driver.get(url)
        time.sleep(30)

        while True:
            try:
                load_more_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[.//span[contains(text(), 'Charger plus')]]")
                    )
                )
                load_more_button.click()
                time.sleep(10)
            except:
                break
        
        exhibitor_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/exposant/']")

        results = []
        for link in exhibitor_links:
            href = link.get_attribute("href")
            try:
                name_element = link.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-gkRewV.cBbmeX.dENBXG")
                name_text = name_element.text.strip()
            except:
                name_text = "No name found"

            results.append({
                "name": name_text,
                "link": href
            })

        output_path = os.path.join(os.getcwd(), f"exhibitors_data/exhibitors_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Successfully saved {len(results)} entries to {output_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_exhibitors()