from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from extraFunctions import getICDDetailsFromEnglishDefinition, getICDDetailsFromSiddhaDefinition, verifyABHAToken
from flask_swagger_ui import get_swaggerui_blueprint
import json


app = Flask(__name__)
CORS(app)   # Enable CORS

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "EMR API"
    }
)


app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory('static', path)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])  # Return empty list if no query

    with open("Data/SiddhaJson.json") as file:
        data = json.load(file)

        # Filter suggestions that start with the query (case-insensitive)
        suggestions = [[item.get("code"), item.get("display"), item.get("designation")[0].get(
            "value")] for item in data.get("concept") if item.get("code").lower().startswith(query)]

        # Limit to 5 suggestions for performance
        suggestions = suggestions[:20]

    return jsonify(suggestions)





@app.route('/api/suggestions/post', methods=['POST'])
def get_suggestions_via_post():
    headers = request.headers
    query = request.get_json() or {}

    # token = headers.get("Authorization", "")
    # if not verifyABHAToken(token):
    #     return jsonify({"error": "Invalid ABHA token"}), 401

    if "code" not in query or "coding" not in query["code"]:
        return jsonify({"error": "Missing code.coding in body"}), 400

    namc_code = query["code"]["coding"][0].get("code", "").lower()

    with open("Data/SiddhaJson.json") as file:
        data = json.load(file)

        suggestions = [
            {
                "code": item.get("code"),
                "display": item.get("display"),
                "designation": item.get("designation")[0].get("value")
            }
            for item in data.get("concept", [])
            if item.get("code", "").lower().startswith(namc_code)
        ][:20]

    return jsonify(suggestions)


@app.route("/api/submit", methods=["POST"])
def submit_term():
    request_data = request.get_json()
    items = request_data.get("term", "").split(",")

    data = getICDDetailsFromEnglishDefinition(items[1])

    # getICDDetailsFromSiddhaDefinition(items[2])

    # res = {"code": "AB",
    #        "english_term": "Jaundice",
    #        "ICD-11": "ME20.1"}

    return jsonify(data)



@app.route('/api/convert/post', methods=['POST'])
def convert():
    headers = request.headers
    query = request.get_json() or {}

    # token = headers.get("Authorization", "")
    # if not verifyABHAToken(token):
    #     return jsonify({"error": "Invalid ABHA token"}), 401

    if "code" not in query or "coding" not in query["code"]:
        return jsonify({"error": "Missing code.coding in body"}), 400

    namc_code = query["code"]["coding"][0].get("code", "").lower()

    with open("Data/SiddhaJson.json") as file:
        data = json.load(file)

        definition = ""
        for item in data.get("concept", []):
            if item.get("code", "").lower() == namc_code.lower():
                definition = item.get("display", "")

    data = getICDDetailsFromEnglishDefinition(definition)

    return jsonify(data)


@app.route("/api/returnJson", methods=["POST"])
def returnJson():
    data = request.get_json()
    print(data)

    icd = data.get("icd")
    namc = data.get("namc")

    

    json_str = f'''{{
      "resourceType": "Condition",
      "id": "cond-123",
      "meta": {{
        "versionId": "1",
        "lastUpdated": "2025-09-10T21:28:00+05:30"
      }},
      "identifier": [
        {{
          "system": "http://abdm.gov.in/ABHA",
          "value": "PAT123456"
        }}
      ],
      "clinicalStatus": {{
        "coding": [
          {{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active"
          }}
        ]
      }},
      "verificationStatus": {{
        "coding": [
          {{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "confirmed"
          }}
        ]
      }},
      "code": {{
        "coding": [
          {{
            "system": "https://ndhm.gov.in/fhir/CodeSystem/namc",
            "code": "{namc.split(',')[0]}",
            "display": "{namc.split(',')[1]}"
          }},
          {{
            "system": "http://id.who.int/icd11/mms",
            "code": "{icd.split(',')[0]}",
            "display": "{icd.split(',')[1]}"
          }}
        ]
      }},
      "subject": {{
        "reference": "Patient/PAT123456",
        "identifier": {{
          "system": "http://abdm.gov.in/ABHA",
          "value": "PAT123456"
        }}
      }},
      "onsetDateTime": "2025-09-10",
      "recordedDate": "2025-09-10T21:28:00+05:30",
      "recorder": {{
        "reference": "Practitioner/DR987654",
        "display": "Dr. Smith"
      }}
    }}'''


    print(json_str)

    return jsonify('"Msg":"Success"')
    

if __name__ == "__main__":

    with app.app_context():
        app.run(debug=True)
