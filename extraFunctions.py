import urllib3
import json
import requests
import  re


def getICDDetailsFromEnglishDefinition(definition, namc_code):

    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '42000a86-ed11-4082-8408-31fe933baa5a_a498c5fb-3ea8-4b0f-b221-05aaacb39be6'
    client_secret = 'aeRcA/gMcEaKLkjxFhLBpbC9UmJmHyuYlK7YWhIPIxw='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    payload = {'client_id': client_id,
               'client_secret': client_secret,
               'scope': scope,
               'grant_type': grant_type}


    print("The token request has been sent")
    r = requests.post(token_endpoint, data=payload).json()
    token = r['access_token']
    print(r['expires_in'])
    print("The token has been received")


    uri = f"https://id.who.int/icd/release/11/2025-01/mms/search?q={definition}"

    headers = {'Authorization':  'Bearer '+token,
               'Accept': 'application/json',
               'Accept-Language': 'en',
               'API-Version': 'v2'}

    print("The WHO api has been called")
    response = requests.get(uri, headers=headers)
    print("The WHO api responded")

    # Raise error if request fails
    response.raise_for_status()

    # Parse JSON
    data = response.json()
    res = [[item.get("theCode"), re.sub(r'<.*?>', '',item.get("title"))]
           for item in data.get("destinationEntities", None)]

    

    if not res:
        print("entered res")
        
        with open("Data/SiddhaJson.json", encoding="utf-8") as file:
            data = json.load(file)

            namc_code = namc_code[:2]
            
            definition = ""
            for item in data.get("concept", []):
                if item.get("code", "").lower() == namc_code.lower():
                    definition = item.get("display", "")
                    break

            r = requests.post(token_endpoint, data=payload).json()
            token = r['access_token']

            uri = f"https://id.who.int/icd/release/11/2025-01/mms/search?q={definition}"

            headers = {'Authorization':  'Bearer '+token,
                       'Accept': 'application/json',
                       'Accept-Language': 'en',
                       'API-Version': 'v2'}
            response = requests.get(uri, headers=headers)

            # Raise error if request fails
            response.raise_for_status()

            # Parse JSON
            data = response.json()
            res = [[item.get("theCode"), re.sub(r'<.*?>', '',item.get("title"))]
                   for item in data.get("destinationEntities", None)]

    return res




def getICDDetailsFromSiddhaDefinition(definition):

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

    uri = f"https://id.who.int/icd/entity/search?q={definition}"

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
        print(d.get("id"))
        response = requests.get(d.get("id"), headers=headers)
        print(response.json())
        



def verifyABHAToken(token):

    # token_id = token.split(" ")[1]
    print(token)


