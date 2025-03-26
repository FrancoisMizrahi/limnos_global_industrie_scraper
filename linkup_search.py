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

linkup_api_key = os.environ['linkup_api_key']

def get_linkedin_profile_linkup(profile: Dict[str, str]) -> Optional[str]:
    """
    Search for a LinkedIn profile using Linkup API for a given profile.
    
    Args:
        profile (Dict[str, str]): Dictionary containing profile information
    
    Returns:
        Optional[str]: LinkedIn profile URL or None if not found
    """
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

def parallel_linkedin_search(profiles: List[Dict[str, str]], max_workers: int = 5) -> List[Optional[str]]:
    """
    Perform parallel LinkedIn profile searches.
    
    Args:
        profiles (List[Dict[str, str]]): List of profiles to search
        max_workers (int, optional): Maximum number of concurrent workers. Defaults to 5.
    
    Returns:
        List[Optional[str]]: List of LinkedIn profile URLs
    """
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
                results.append(linkedin_url)
                
                # Optional: print results as they come in
                print(f"Profile {profile}: {linkedin_url}")
            
            except Exception as e:
                print(f"Error processing profile {profile}: {e}")
        
        return results

if __name__ == "__main__":
    # Example list of profiles to search
    profiles = [
        {"Name": "Francois Mizrahi", "Position": "CEO", "Company": "Limnos"},
        {"Name": "Leopold du breuil", "Position": "COO", "Company": "Limnos"},
    ]
    
    # Perform parallel search
    linkedin_profiles = parallel_linkedin_search(profiles)
    
    # Print final results
    print("\nFinal LinkedIn Profiles:")
    for profile in linkedin_profiles:
        print(profile)