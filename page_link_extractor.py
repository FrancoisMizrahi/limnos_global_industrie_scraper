import time
import json
import os
from datetime import datetime


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_exhibitors():
    # 1) Start Selenium (Chrome in this example)
    driver = webdriver.Chrome()

    try:
        # 2) Open the exhibitor list page
        url = "https://www.global-industrie.com/liste-des-exposants"
        driver.get(url)

        # 3) Wait briefly for the page to load
        time.sleep(30)

        # 4) Keep clicking "Charger plus" until no more are found or clickable
        while True:
            try:
                # Wait up to 5 seconds for the button
                load_more_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[.//span[contains(text(), 'Charger plus')]]")
                    )
                )
                load_more_button.click()
                time.sleep(10)  # short pause to let new items load
            except:
                # If we can't find/click the button, assume we're at the end
                break

        # 5) Now all exhibitors should be visible. Let's grab them.
        #    We'll select every <a> whose href contains "/exposant/" 
        exhibitor_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/exposant/']")

        results = []
        for link in exhibitor_links:
            # Extract the href from the <a>
            href = link.get_attribute("href")

            # Extract the text from the name span
            #   Example from your HTML:
            #      <span class="sc-esYiGF sc-gkRewV cBbmeX dENBXG">ACTIMETAL INDUSTRIE</span>
            try:
                name_element = link.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-gkRewV.cBbmeX.dENBXG")
                name_text = name_element.text.strip()
            except:
                name_text = "No name found"

            results.append({
                "name": name_text,
                "link": href
            })

        # 6) Write everything to a JSON file in the same directory as this script
        output_path = os.path.join(os.getcwd(), f"exhibitors_data/exhibitors_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Successfully saved {len(results)} entries to {output_path}")

    finally:
        # 7) Close the browser
        driver.quit()

if __name__ == "__main__":
    scrape_exhibitors()