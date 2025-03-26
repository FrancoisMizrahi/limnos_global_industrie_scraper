import os
import requests
import json
import openai


openai_api_key = os.environ['openai_api_key']
notion_token = os.environ['notion_token']


with open('exhibitors_data/people_pages.json') as f:
    people_pages = json.load(f)

b2b_roles = [
    "Other position",
    "CEO",
    "Directeur général",
    "Directeur commercial",
    "Directeur des opérations (COO)",
    "Directeur marketing (CMO)",
    "Directeur technique",
    "Directeur administratif et financier (DAF)",
    "Directeur de business unit",
    "Directeur du développement",
    "Directeur des ventes",
    "Responsable commercial",
    "Responsable grands comptes (Key Account Manager)",
    "Account Manager",
    "Technical Sales Manager",
    "Sales Engineer",
    "Technico-commercial",
    "Commercial",
    "Commercial sédentaire",
    "Sales & Marketing Manager",
    "Business Development Manager",
    "Sales Representative",
    "Responsable développement commercial",
    "Responsable partenariats",
    "Ingénieur",
    "Ingénieur commercial",
    "Ingénieur d’études",
    "Responsable technique",
    "Ingénieur applications",
    "Ingénieur R&D",
    "Responsable bureau d'études",
    "Responsable industrialisation",
    "Responsable méthodes",
    "Responsable maintenance",
    "Chef de projet technique",
    "Chef de produit",
    "Responsable produit",
    "Technical Product Manager",
    "Chef de projet / Project Manager",
    "Chargé d’affaires",
    "Responsable innovation",
    "Responsable projets",
    "Bid Manager",
    "Solution Engineer",
    "Application Engineer",
    "Chief Marketing Officer (CMO)",
    "Responsable marketing",
    "Responsable communication",
    "Chargé de marketing digital",
    "Marketing & Communication Manager",
    "Responsable achats",
    "Responsable qualité",
    "Responsable ADV",
    "Administration des ventes (ADV)",
    "Responsable supply chain",
    "Responsable ressources humaines (RH)"
]

client = openai.Client(api_key=openai_api_key)

def generate_text_with_gpt4(role):
    """Generates text using the GPT-4 model."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful B2B sales assistant that classifies positions correctly."},
            {"role": "assistant", "content": f"The different positions possible are the following: {b2b_roles}"},
            {"role": "user", "content": f"What of the possible positions matches best the following role? only output the most likely role and noting else. Do not output quotes like (') \n The role to classify: {role}"}
        ]
    )
    return response.choices[0].message.content


def update_member_page(page_id, existing_positions, clean_positions):
  updated_properties = {
      "Position category": {"multi_select": [{'name': position.lower()} for position in clean_positions]},
      "Position Original": {"rich_text": [{"text": {"content": ", ".join(existing_positions)[:2000]}}]},
      }

  url = f"https://api.notion.com/v1/pages/{page_id}"
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


def update_members_positions(people_pages):
  for page in people_pages:
    page_id = page["id"]
    
    existing_positions = []
    clean_positions = []

    for position in page["properties"]["Position"]["multi_select"]:
      existing_positions.append(position["name"])
      clean_position = generate_text_with_gpt4(position["name"])
      print(f"chatGPT: {clean_position} - original: {position['name']}")
      clean_positions.append(clean_position)

    update_member_page(page_id, existing_positions, clean_positions)


update_members_positions(people_pages[:20])