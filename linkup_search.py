# import os
# from linkup import LinkupClient

# linkup_api_key = os.environ['linkup_api_key']

# def get_linkedin_profile_linkup(profile):
#     client = LinkupClient(api_key=linkup_api_key)

#     response = client.search(
#         query=f"Find me the linkedin profile of this person: {profile}",
#         depth="standard",
#         output_type="structured",
#         structured_output_schema="{\"type\": \"object\",\"properties\": {\"LinkedIn\": {\"type\": \"string\",\"description\": \"Linkedin Profile URL\"}}}"
#     )

#     return response

# if __name__ == "__main__":
#     profile = {
#         "Name": "Francois Mizrahi",
#         "Position": "CEO",
#         "Company": "Limnos"
#     }
#     response = get_linkedin_profile_linkup(profile)
#     print(response["LinkedIn"])



import os
import concurrent.futures
from linkup import LinkupClient
from typing import Dict, List, Optional
import json
import requests
import time
from tqdm import tqdm


linkup_api_key = os.environ['linkup_api_key']
notion_token = os.environ['notion_token']

with open('exhibitors_data/people_pages.json') as f:
    people_pages = json.load(f)

with open('exhibitors_data/company_ids.json') as f:
    companies_id = json.load(f)
    ids_company = {value: key for key, value in companies_id.items()}


def prep_linkup_data(people_pages):
    profiles = []
    for page in people_pages:
        data = {}
        data["id"] = page["id"]
        data["Name"] = page["properties"]["Name"]["title"][0]["plain_text"]
        data["Position"] = ", ".join([position["name"] for position in page["properties"]["Position"]["multi_select"]])
        data["Company"] = ids_company[page["properties"]["Company CRM"]["relation"][0]["id"]]
        profiles.append(data)
    return profiles



def get_linkedin_profile_linkup(profile: Dict[str, str]) -> Optional[str]:
    client = LinkupClient(api_key=linkup_api_key)

    try:
        response = client.search(
            query=f"Find me the linkedin profile of this person: {profile}",
            depth="standard",
            output_type="structured",
            structured_output_schema="{\"type\": \"object\",\"properties\": {\"LinkedIn\": {\"type\": \"string\",\"description\": \"Linkedin Profile URL\"}}}"
        )
        
        # Return the LinkedIn profile URL or None
        return response.get("LinkedIn")
    
    except Exception as e:
        print(f"Error searching for {profile}: {e}")
        return None

def parallel_linkedin_search(profiles: List[Dict[str, str]], max_workers: int = 50) -> List[Optional[str]]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit search tasks for each profile
        future_to_profile = {
            executor.submit(get_linkedin_profile_linkup, profile): profile 
            for profile in profiles
        }
        
        # Collect results as they complete
        results = []
        for future in concurrent.futures.as_completed(future_to_profile):
            profile = future_to_profile[future]
            try:
                linkedin_url = future.result()
                profile["LinkedIn"] = linkedin_url
                results.append(profile)
            except Exception as e:
                print(f"Error processing profile {profile}: {e}")
        
        return results



def update_member_page_with_linkedin(result):
  updated_properties = {
      "LinkedIn URL": {"url": result["LinkedIn"] if result["LinkedIn"] else None},
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


def update_members_page_with_linkedin(results):
  start_point = 0
  for result in tqdm(results, desc="Processing"):
    update_member_page_with_linkedin(result)
    print(start_point)
    print(result)
    start_point += 1



if __name__ == "__main__":
    tic = time.time()
    profiles = prep_linkup_data(people_pages[2000:])
    results = parallel_linkedin_search(profiles)
    with open('exhibitors_data//profiles_linkup_enhanced.json', 'w') as fp:
        json.dump(results, fp)
    # update_members_page_with_linkedin(results)
    toc = time.time()
    print(toc - tic)

