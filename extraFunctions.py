import urllib3
import json
import requests


def getICDDetailsFromEnglishDefinition(defintion):

    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '42000a86-ed11-4082-8408-31fe933baa5a_a498c5fb-3ea8-4b0f-b221-05aaacb39be6'
    client_secret = 'aeRcA/gMcEaKLkjxFhLBpbC9UmJmHyuYlK7YWhIPIxw='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    payload = {'client_id': client_id,
               'client_secret': client_secret,
               'scope': scope,
               'grant_type': grant_type}

    r = requests.post(token_endpoint, data=payload).json()
    token = r['access_token']

    uri = f"https://id.who.int/icd/release/11/2025-01/mms/search?q={defintion}"

    headers = {'Authorization':  'Bearer '+token,
               'Accept': 'application/json',
               'Accept-Language': 'en',
               'API-Version': 'v2'}

    response = requests.get(uri, headers=headers)

    # Raise error if request fails
    response.raise_for_status()

    # Parse JSON
    data = response.json()

    res = [[item.get("theCode"), item.get("title")]
           for item in data.get("destinationEntities", None)]

    # for item in data.get("destinationEntities", None):
    #     var = {"code": item.get("theCode"),
    #            "english_term": item.get("title"),
    #            }
    #     res.append(var)
    #
    # for r in res:
    #     print(r)

    return res




def getICDDetailsFromSiddhaDefinition(defintion):

    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '42000a86-ed11-4082-8408-31fe933baa5a_a498c5fb-3ea8-4b0f-b221-05aaacb39be6'
    client_secret = 'aeRcA/gMcEaKLkjxFhLBpbC9UmJmHyuYlK7YWhIPIxw='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    payload = {'client_id': client_id,
               'client_secret': client_secret,
               'scope': scope,
               'grant_type': grant_type}

    r = requests.post(token_endpoint, data=payload).json()
    token = r['access_token']

    uri = f"https://id.who.int/icd/entity/search?q={defintion}"

    headers = {'Authorization':  'Bearer '+token,
               'Accept': 'application/json',
               'Accept-Language': 'en',
               'API-Version': 'v2'}

    response = requests.get(uri, headers=headers)

    # Raise error if request fails
    response.raise_for_status()

    # Parse JSON
    data = response.json()

    # res = [[item.get("theCode"), item.get("title")]
    #        for item in data.get("destinationEntities", None)]

    print(data)


    for d in data.get("destinationEntities"):
        print(d)



