import os
import json
import requests
from bs4 import BeautifulSoup






# # 1) Load links from exhibitors.json
# with open("exhibitors.json", "r", encoding="utf-8") as f:
#     exhibitor_list = json.load(f)

# results = []

# for item in exhibitor_list[:1]:
#     link = item.get("link")
#     print(link)
#     if not link:
#         # Skip entries that have no link
#         continue

#     # 2) Fetch the page via requests
#     response = requests.get(link)
#     if response.status_code != 200:
#         print(f"Failed to fetch {link} - status code {response.status_code}")
#         continue

#     soup = BeautifulSoup(response.text, "html.parser")

#     print(soup.select_one("h1.hero__title"))
#     print(soup.select_one("a.sc-jXbUNg"))










from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Set up the Chrome driver (update the path to your chromedriver if needed)
driver = webdriver.Chrome()

# 1) Load links from exhibitors.json
with open("exhibitors.json", "r", encoding="utf-8") as f:
    exhibitor_list = json.load(f)

results = []

for item in exhibitor_list[:10]:
    link = item.get("link")
    # 2. Open the desired web page
    driver.get(link)

    # 3. Wait until the document is fully loaded
    #    - The lambda checks that the 'document.readyState' is 'complete'.
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # 4. Grab the HTML content
    page_source = driver.page_source

    # 5. Write the HTML to a file
    with open(f"test_html/{item.get("name")}.html", "w", encoding="utf-8") as file:
        file.write(page_source)

# 6. Clean up and close the browser
driver.quit()































# def scrape_exhibitors_from_links_bs():
#     # 1) Load links from exhibitors.json
#     with open("exhibitors.json", "r", encoding="utf-8") as f:
#         exhibitor_list = json.load(f)

#     results = []

#     for item in exhibitor_list[:3]:
#         link = item.get("link")
#         if not link:
#             # Skip entries that have no link
#             continue

#         # 2) Fetch the page via requests
#         response = requests.get(link)
#         if response.status_code != 200:
#             print(f"Failed to fetch {link} - status code {response.status_code}")
#             continue

#         soup = BeautifulSoup(response.text, "html.parser")

#         record = {}

#         # --- Company Name (e.g., <h1 class="sc-guNwuy crpMCq">...) ---
#         name_elem = soup.select_one("h1.sc-guNwuy.crpMCq")
#         record["companyName"] = name_elem.get_text(strip=True) if name_elem else ""

#         # --- Company Type (e.g., <h2 class="sc-cdSkuB fhQCke">Exposants</h2>) ---
#         type_elem = soup.select_one("h2.sc-cdSkuB.fhQCke")
#         record["companyType"] = type_elem.get_text(strip=True) if type_elem else ""

#         # --- Booth Number (e.g., <span class="sc-bzUlqy bUxMas">3F204</span>) ---
#         booth_elem = soup.select_one("span.sc-bzUlqy.bUxMas")
#         record["boothNumber"] = booth_elem.get_text(strip=True) if booth_elem else ""

#         # --- Information / Description (e.g., <div class="sc-faJNnW ftfZCw">...) ---
#         info = {}
#         info_elem = soup.select_one("div.sc-faJNnW.ftfZCw")
#         info["description"] = info_elem.get_text("\n", strip=True) if info_elem else ""
#         record["information"] = info

#         # --- Activities & Regions ---
#         record["activities"] = {}
#         record["regions"] = []

#         # In the Selenium approach, we used XPaths for a block containing text “Activités / Régions”.
#         # In BeautifulSoup, we can locate by heading text or by distinctive classes.
#         # We'll search for the <div class="sc-cJIyfF cvMBHw"> that also has a child
#         #   <div class="sc-hfAwGc cKDOHH">Activités / Régions</div>.
#         # We'll do a two-step approach: find all .sc-cJIyfF.cvMBHw blocks, then check if it contains that heading.

#         ar_block = None
#         blocks = soup.select("div.sc-cJIyfF.cvMBHw")
#         for b in blocks:
#             heading = b.select_one("div.sc-hfAwGc.cKDOHH")
#             if heading and "Activités / Régions" in heading.get_text(strip=True):
#                 ar_block = b
#                 break

#         if ar_block:
#             # <li class="sc-jbPfzJ gOXooL"> structure
#             li_elements = ar_block.select("li.sc-jbPfzJ.gOXooL")
#             for li in li_elements:
#                 # e.g. <div class="sc-PXPPG ftmBgu">Activité</div>
#                 heading_div = li.select_one("div.sc-PXPPG.ftmBgu")
#                 heading_text = heading_div.get_text(strip=True) if heading_div else ""

#                 if heading_text == "Activité":
#                     # The child <ul> has categories
#                     sub_li_elems = li.select(":scope > ul li.sc-jbPfzJ.gOXooL")
#                     for sub_li in sub_li_elems:
#                         cat_div = sub_li.select_one("div.sc-PXPPG.ftmBgu")
#                         category_name = cat_div.get_text(strip=True) if cat_div else ""
#                         if category_name:
#                             # sub-sub items
#                             sub_sub_lis = sub_li.select(":scope > ul li.sc-jbPfzJ.gOXooL")
#                             sub_items = []
#                             for s in sub_sub_lis:
#                                 s_div = s.select_one("div.sc-PXPPG.ftmBgu")
#                                 if s_div:
#                                     sub_items.append(s_div.get_text(strip=True))
#                             record["activities"][category_name] = sub_items

#                 elif heading_text == "Régions":
#                     # parse all region <li>
#                     region_li_elems = li.select(":scope > ul li.sc-jbPfzJ.gOXooL")
#                     for region_li in region_li_elems:
#                         region_div = region_li.select_one("div.sc-PXPPG.ftmBgu")
#                         if region_div:
#                             record["regions"].append(region_div.get_text(strip=True))

#         # --- Univers ---
#         record["univers"] = ""
#         univers_block = None
#         for b in blocks:
#             heading = b.select_one("div.sc-hfAwGc.cKDOHH")
#             if heading and heading.get_text(strip=True) == "Univers":
#                 univers_block = b
#                 break

#         if univers_block:
#             ub_elem = univers_block.select_one("div.sc-daNmkL.fBOHHx")
#             if ub_elem:
#                 record["univers"] = ub_elem.get_text(strip=True)

#         # --- Thématique ---
#         record["thematique"] = []
#         thematique_block = None
#         for b in blocks:
#             heading = b.select_one("div.sc-hfAwGc.cKDOHH")
#             if heading and heading.get_text(strip=True) == "Thématique":
#                 thematique_block = b
#                 break

#         if thematique_block:
#             # might have <span class="sc-dfzyxB"> entries
#             thematique_spans = thematique_block.select("div.sc-goaFza.fHgcaR span.sc-dfzyxB")
#             record["thematique"] = [sp.get_text(strip=True) for sp in thematique_spans]

#         # --- Pays ---
#         record["pays"] = ""
#         pays_block = None
#         for b in blocks:
#             heading = b.select_one("div.sc-hfAwGc.cKDOHH")
#             if heading and heading.get_text(strip=True) == "Pays":
#                 pays_block = b
#                 break
#         if pays_block:
#             pb_elem = pays_block.select_one("div.sc-daNmkL.fBOHHx")
#             if pb_elem:
#                 record["pays"] = pb_elem.get_text(strip=True)

#         # --- Contact Details (Détails du contact) ---
#         contact_details = {}
#         contact_block = None
#         # Another approach is to look for <h2 class="sc-cwHptR kwKDni">Détails du contact</h2> 
#         # then get the parent block
#         contact_parent = soup.find("h2", class_="sc-cwHptR kwKDni", string="Détails du contact")
#         if contact_parent:
#             # The parent might be .sc-djPPSU foApFf or a few containers up
#             # We'll just walk upward or find a sibling
#             # Quick approach: go up two or three levels:
#             contact_block = contact_parent.find_parent("div", class_="sc-djPPSU")
        
#         if contact_block:
#             # The "website" link is typically an <a> that is NOT a Google Maps link
#             # The "address" link is an <a> that DOES contain "maps".
#             website_a = contact_block.find("a", href=lambda x: x and "maps" not in x)
#             address_a = contact_block.find("a", href=lambda x: x and "maps" in x)

#             contact_details["website"] = website_a.get_text(strip=True) if website_a else ""
#             contact_details["address"] = address_a.get_text(strip=True) if address_a else ""
#         record["contactDetails"] = contact_details

#         # --- Team Members (Membres de l'équipe) ---
#         # There's a <div id="team">. Each member is in a .sc-dwalKd block
#         record["teamMembers"] = []
#         team_div = soup.find("div", id="team")
#         if team_div:
#             member_blocks = team_div.find_all("div", class_="sc-dwalKd")
#             for mb in member_blocks:
#                 t_name = ""
#                 t_position = ""
#                 t_company = ""

#                 # name is in <span class="sc-esYiGF sc-dUYLmH ...">
#                 name_span = mb.select_one("span.sc-esYiGF.sc-dUYLmH")
#                 if name_span:
#                     t_name = name_span.get_text(strip=True)

#                 # position is in <span class="sc-esYiGF sc-cezyBN ...">
#                 position_span = mb.select_one("span.sc-esYiGF.sc-cezyBN")
#                 if position_span:
#                     t_position = position_span.get_text(strip=True)

#                 # company is in <span class="sc-esYiGF sc-fUkmAC ...">
#                 company_span = mb.select_one("span.sc-esYiGF.sc-fUkmAC")
#                 if company_span:
#                     t_company = company_span.get_text(strip=True)

#                 record["teamMembers"].append({
#                     "name": t_name,
#                     "position": t_position,
#                     "company": t_company
#                 })

#         results.append(record)
#         print(f"Scraped: {record['companyName']} (link: {link})")

#     # 3) Write all data to exhibitors_detailed.json
#     output_path = os.path.join(os.getcwd(), "exhibitors_detailed.json")
#     with open(output_path, "w", encoding="utf-8") as out_f:
#         json.dump(results, out_f, ensure_ascii=False, indent=2)

#     print(f"\nDone! Wrote {len(results)} exhibitor details to {output_path}")

# if __name__ == "__main__":
#     scrape_exhibitors_from_links_bs()
