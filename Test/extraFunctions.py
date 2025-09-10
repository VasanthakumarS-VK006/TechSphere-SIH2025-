import requests
import json

def getICDDetailsFromEnglishDefinition(definition):
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '42000a86-ed11-4082-8408-31fe933baa5a_a498c5fb-3ea8-4b0f-b221-05aaacb39be6'
    client_secret = 'aeRcA/gMcEaKLkjxFhLBpbC9UmJmHyuYlK7YWhIPIxw='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    payload = {'client_id': client_id, 'client_secret': client_secret, 'scope': scope, 'grant_type': grant_type}
    r = requests.post(token_endpoint, data=payload).json()
    token = r['access_token']

    uri = f"https://id.who.int/icd/release/11/2025-01/mms/search?q={definition}"
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Accept-Language': 'en', 'API-Version': 'v2'}
    response = requests.get(uri, headers=headers)
    response.raise_for_status()
    data = response.json()
    res = [[item.get("theCode"), item.get("title")] for item in data.get("destinationEntities", [])]
    return res  # Returns [[code, title], ...] for Biomedicine/TM matches

def getICDDetailsFromSiddhaDefinition(definition):  # Fixed to use parameter
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '42000a86-ed11-4082-8408-31fe933baa5a_a498c5fb-3ea8-4b0f-b221-05aaacb39be6'
    client_secret = 'aeRcA/gMcEaKLkjxFhLBpbC9UmJmHyuYlK7YWhIPIxw='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    payload = {'client_id': client_id, 'client_secret': client_secret, 'scope': scope, 'grant_type': grant_type}
    r = requests.post(token_endpoint, data=payload).json()
    token = r['access_token']

    uri = f"https://id.who.int/icd/entity/search?q={definition}"  # Fixed to use definition
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Accept-Language': 'en', 'API-Version': 'v2'}
    response = requests.get(uri, headers=headers)
    response.raise_for_status()
    data = response.json()
    res = []
    for item in data.get("destinationEntities", []):
        entity_uri = item.get("id")
        entity_response = requests.get(entity_uri, headers=headers)
        entity_data = entity_response.json()
        res.append({"code": item.get("theCode"), "title": item.get("title"), "details": entity_data})
    return res
