import json
import pandas as pd
import requests
import os


notion_token = os.environ['notion_token']
database_id = os.environ['database_id']

def add_row_to_notion_database(data):
    try:
        response = requests.post(data["url"], headers=data["headers"], json=data["payload"])
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error adding row: {e}")
        if response is not None:
            print(f"Response body: {response.text}")
        return None


with open('exhibitors_data/company_ids.json') as f:
    company_ids = json.load(f)
    
df_members = pd.read_csv("exhibitors_data/global_industries_company_members_full.csv")
df_members['Position'] = df_members['Position'].apply(lambda x: [item.strip() for item in str(x).split(',')] if isinstance(x, str) else [])
members_list = df_members.to_dict('records')

for member in members_list:
  member["company_crm_page_id"] = company_ids.get(str(member["Company CRM"]).lower())

def create_notion_data_members(row):
    properties = {
            "Name": {"title": [{"text": {"content": row["Name"]}}]},
            "Position": {"multi_select": [{'name': position.lower()} for position in row['Position']]},
            "Status": {"status": {"name": "Lead"}},
            "Company CRM": {"relation": [{"id": row["company_crm_page_id"]}]},
            "Priority": {"select": {"name": "Low"}},
            "Next Step": {"select": {"name": "Qualify"}},
        }
    return {
      "url": "https://api.notion.com/v1/pages",
      "headers": {
          "Authorization": f"Bearer {notion_token}",
          "Content-Type": "application/json",
          "Notion-Version": "2022-06-28",
      },
      "payload": {
          "parent": {"database_id": database_id},
          "properties": properties,
      }
      }


for member in members_list:
  data = create_notion_data_members(member)
  add_row_to_notion_database(data)