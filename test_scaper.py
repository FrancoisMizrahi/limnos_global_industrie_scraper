import time
import json
import os

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
        output_path = os.path.join(os.getcwd(), "exhibitors.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Successfully saved {len(results)} entries to {output_path}")

    finally:
        # 7) Close the browser
        driver.quit()



def scrape_exhibitors_from_links():
    # 1. Load links from exhibitors.json
    with open("exhibitors.json", "r", encoding="utf-8") as f:
        exhibitor_list = json.load(f)

    # Initialize Selenium (Chrome)
    driver = webdriver.Chrome()

    results = []
    try:
        # 2. For each exhibitor in the JSON, visit the link and scrape
        for item in exhibitor_list[:10]:
            link = item.get("link")
            if not link:
                # Skip if no link found
                continue

            driver.get(link)
            time.sleep(2)  # Let page load briefly

            record = {}

            # --- Company Name ---
            try:
                company_name_elem = driver.find_element(By.CSS_SELECTOR, "h1.sc-guNwuy.crpMCq")
                record["companyName"] = company_name_elem.text.strip()
            except:
                record["companyName"] = ""

            # --- Company Type ---
            try:
                company_type_elem = driver.find_element(By.CSS_SELECTOR, "h2.sc-cdSkuB.fhQCke")
                record["companyType"] = company_type_elem.text.strip()
            except:
                record["companyType"] = ""

            # --- Booth Number ---
            try:
                booth_elem = driver.find_element(By.CSS_SELECTOR, "span.sc-bzUlqy.bUxMas")
                record["boothNumber"] = booth_elem.text.strip()
            except:
                record["boothNumber"] = ""

            # --- Information (description) ---
            info = {}
            try:
                info_elem = driver.find_element(By.CSS_SELECTOR, "div.sc-faJNnW.ftfZCw")
                info["description"] = info_elem.text.strip()
            except:
                info["description"] = ""
            record["information"] = info

            # --- Activities / Regions ---
            record["activities"] = {}
            record["regions"] = []
            try:
                block_xpath = "//div[@class='sc-cJIyfF cvMBHw'][.//div[@class='sc-hfAwGc cKDOHH' and contains(text(),'Activités / Régions')]]"
                activities_regions_block = driver.find_element(By.XPATH, block_xpath)

                li_elements = activities_regions_block.find_elements(By.CSS_SELECTOR, "li.sc-jbPfzJ.gOXooL")
                for li in li_elements:
                    heading_text = ""
                    try:
                        heading_div = li.find_element(By.CSS_SELECTOR, "div.sc-PXPPG.ftmBgu")
                        heading_text = heading_div.text.strip()
                    except:
                        pass

                    if heading_text == "Activité":
                        # Parse all activity categories
                        sub_li_elems = li.find_elements(By.CSS_SELECTOR, ":scope > ul li.sc-jbPfzJ.gOXooL")
                        for sub_li in sub_li_elems:
                            try:
                                cat_div = sub_li.find_element(By.CSS_SELECTOR, "div.sc-PXPPG.ftmBgu")
                                category_name = cat_div.text.strip()
                            except:
                                continue

                            # Inside each category, you might find sub-sub items
                            sub_sub_lis = sub_li.find_elements(By.CSS_SELECTOR, ":scope > ul li.sc-jbPfzJ.gOXooL")
                            sub_items = []
                            for s in sub_sub_lis:
                                try:
                                    txt = s.find_element(By.CSS_SELECTOR, "div.sc-PXPPG.ftmBgu").text.strip()
                                    sub_items.append(txt)
                                except:
                                    pass

                            record["activities"][category_name] = sub_items

                    elif heading_text == "Régions":
                        # Parse region(s)
                        region_li_elems = li.find_elements(By.CSS_SELECTOR, ":scope > ul li.sc-jbPfzJ.gOXooL")
                        for region_li in region_li_elems:
                            try:
                                region_div = region_li.find_element(By.CSS_SELECTOR, "div.sc-PXPPG.ftmBgu")
                                region_text = region_div.text.strip()
                                record["regions"].append(region_text)
                            except:
                                pass
            except:
                pass

            # --- Univers ---
            record["univers"] = ""
            try:
                univers_block_xpath = "//div[@class='sc-cJIyfF cvMBHw'][.//div[@class='sc-hfAwGc cKDOHH' and text()='Univers']]"
                univers_block = driver.find_element(By.XPATH, univers_block_xpath)
                univers_text_elem = univers_block.find_element(By.CSS_SELECTOR, "div.sc-daNmkL.fBOHHx")
                record["univers"] = univers_text_elem.text.strip()
            except:
                pass

            # --- Thématique ---
            record["thematique"] = []
            try:
                thematique_block_xpath = "//div[@class='sc-cJIyfF cvMBHw'][.//div[@class='sc-hfAwGc cKDOHH' and text()='Thématique']]"
                thematique_block = driver.find_element(By.XPATH, thematique_block_xpath)
                spans = thematique_block.find_elements(By.CSS_SELECTOR, "div.sc-goaFza.fHgcaR span.sc-dfzyxB")
                record["thematique"] = [s.text.strip() for s in spans]
            except:
                pass

            # --- Pays ---
            record["pays"] = ""
            try:
                pays_block_xpath = "//div[@class='sc-cJIyfF cvMBHw'][.//div[@class='sc-hfAwGc cKDOHH' and text()='Pays']]"
                pays_block = driver.find_element(By.XPATH, pays_block_xpath)
                pays_elem = pays_block.find_element(By.CSS_SELECTOR, "div.sc-daNmkL.fBOHHx")
                record["pays"] = pays_elem.text.strip()
            except:
                pass

            # --- Contact Details ---
            contact_details = {}
            try:
                contact_xpath = "//div[h2[@class='sc-cwHptR kwKDni' and text()='Détails du contact']]"
                contact_block = driver.find_element(By.XPATH, contact_xpath)

                # website
                try:
                    website_link = contact_block.find_element(By.XPATH, ".//a[not(contains(@href, 'maps'))]")
                    contact_details["website"] = website_link.text.strip()
                except:
                    contact_details["website"] = ""

                # address (google maps link)
                try:
                    address_link = contact_block.find_element(By.XPATH, ".//a[contains(@href, 'maps')]")
                    contact_details["address"] = address_link.text.strip()
                except:
                    contact_details["address"] = ""
            except:
                pass
            record["contactDetails"] = contact_details

            # --- Team Members ---
            team = []
            try:
                team_container = driver.find_element(By.ID, "team")
                member_blocks = team_container.find_elements(By.XPATH, ".//div[contains(@class,'sc-dwalKd')]")
                for mb in member_blocks:
                    t_name = ""
                    t_position = ""
                    t_company = ""

                    try:
                        name_elem = mb.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-dUYLmH")
                        t_name = name_elem.text.strip()
                    except:
                        pass

                    try:
                        position_elem = mb.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-cezyBN")
                        t_position = position_elem.text.strip()
                    except:
                        pass

                    try:
                        company_elem = mb.find_element(By.CSS_SELECTOR, "span.sc-esYiGF.sc-fUkmAC")
                        t_company = company_elem.text.strip()
                    except:
                        pass

                    team.append({
                        "name": t_name,
                        "position": t_position,
                        "company": t_company
                    })
            except:
                pass
            record["teamMembers"] = team

            results.append(record)
            print(f"Scraped details for: {record['companyName']}")

    finally:
        driver.quit()

    # 3. Save results to exhibitors_detailed.json
    output_path = os.path.join(os.getcwd(), "exhibitors_detailed.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Done! Wrote {len(results)} entries to {output_path}")

if __name__ == "__main__":
    # scrape_exhibitors()
    scrape_exhibitors_from_links()
