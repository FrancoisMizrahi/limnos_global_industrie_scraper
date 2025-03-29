import os
import json
import requests
import time
from tqdm import tqdm


notion_token = os.environ['notion_token']

def get_data():
    with open('exhibitors_data/people_pages.json') as f:
        people_pages = json.load(f)

    with open('exhibitors_data/company_ids.json') as f:
        companies_id = json.load(f)
        ids_company = {value: key for key, value in companies_id.items()}
    
    return people_pages, ids_company


def find_company_name(people_pages, ids_company):
    results = []
    for people in people_pages:
        data = {}
        data["id"] = people["id"]
        data["company_name"] = ids_company[people["properties"]["Company CRM"]["relation"][0]["id"]]
        results.append(data)
    return results


def update_member_page_with_company_name(result):
  updated_properties = {
      "Company name": {"select": {"name": result["company_name"].replace(",", "") if result["company_name"] else None}},
      }

  url = f"https://api.notion.com/v1/pages/{result['id']}"
  headers = {
      "Authorization": f"Bearer {notion_token}",
      "Content-Type": "application/json",
      "Notion-Version": "2022-06-28"
  }

  payload = {"properties": updated_properties}
  response = requests.patch(url, headers=headers, data=json.dumps(payload))

  if response.status_code == 200:
    pass
  else:
      print(f"Failed to update. Status: {response.status_code}")
      print(response.text)


def update_members_page(results, start_point):
  for result in tqdm(results[start_point:], desc="Processing"):
    update_member_page_with_company_name(result)
    print(start_point)
    print(result)
    start_point += 1


if __name__ == "__main__":
    tic = time.time()
    people_pages, ids_company = get_data()
    results = find_company_name(people_pages, ids_company)
    update_members_page(results, 2000)
    toc = time.time()
    print(toc - tic)
