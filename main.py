from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from extraFunctions import getICDDetailsFromEnglishDefinition, getICDDetailsFromSiddhaDefinition, verifyABHAToken, findNAMCTerm
from flask_swagger_ui import get_swaggerui_blueprint
import json
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# --- Default Codes for Logging ---
DEFAULT_DOCTOR_CODE = "DR987654"
DEFAULT_PATIENT_CODE = "PAT123456"
# --------------------------------

# --- Custom Log File for Search Activity ---
LOG_FILE_NAME = "search_log.txt"


def log_search_activity(search_term, result_summary):
    """Logs doctor/patient IDs and search activity to a simple text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"Timestamp: {timestamp} | "
        f"DoctorID: {DEFAULT_DOCTOR_CODE} | "
        f"PatientID: {DEFAULT_PATIENT_CODE} | "
        f"SearchTerm: {search_term} | "
        f"Result: {result_summary}\n"
    )
    try:
        with open(LOG_FILE_NAME, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")
# ---------------------------------------------


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "EMR API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route("/swagger.json")
def swagger_json():


    swagger_data = {
  "openapi": "3.0.3",
  "info": {
    "title": "EMR API",
    "description": "API demo combining FHIR Condition resource (NAMC + ICD-11).",
    "version": "1.0.0",
    "license": {
      "name": "MIT",
      "url": "https://opensource.org/licenses/MIT"
    }
  },
  "servers": [
    {
      "url": url_for("swagger_json", _external=True).replace("/swagger.json", ""),
      "description": "Local development server"
    }
  ],
  "tags": [
    {
      "name": "Condition Request",
      "description": "Create FHIR Condition resources"
    },
  ],
  "paths": {
    "/convert/post": {
      "get": {
        "tags": ["NAMC Convertion"],
        "summary": "Returns ICD Code",
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "schema": { "type": "integer", "default": 10 }
          },
          {
            "name": "sort",
            "in": "query",
            "schema": { "type": "string", "enum": ["asc", "desc"] }
          },
          {
            "name": "search",
            "in": "query",
            "schema": { "type": "string" }
          }
        ],
        "responses": {
          "200": {
            "description": "OK",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/bookRequests" }
              }
            }
          }
        }
      },

      "post": {
        "tags": ["Condition Request"],
        "summary": "Create a FHIR Condition resource",
        "description": "Creates a Condition resource with NAMC + ICD-11 codes.",
        "parameters": [
          {
            "name": "token",
            "in": "header",
            "schema": { "type": "string", "default": "abha-1294875" }
          }
        ],
        "requestBody": {
          "description": "Condition resource to create",
          "required": true,
          "content": {
            "application/json": {
              "schema": { "$ref": "#/components/schemas/Condition" }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Condition created successfully",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/Condition" }
              }
            }
          },
          "400": {
            "description": "Invalid request",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/OperationOutcome" }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Condition": {
        "type": "object",
        "properties": {
          "resourceType": { "type": "string", "example": "Condition" },
          "id": { "type": "string", "example": "789" },
          "meta": {
            "type": "object",
            "properties": {
              "versionId": { "type": "string", "example": "1" },
              "lastUpdated": {
                "type": "string",
                "format": "date-time",
                "example": "2025-09-10T06:48:00+05:30"
              }
            }
          },
          "identifier": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "system": { "type": "string", "example": "http://abdm.gov.in/ABHA" },
                "value": { "type": "string", "example": "123456" }
              }
            }
          },
          "clinicalStatus": {
            "type": "object",
            "properties": {
              "coding": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "system": {
                      "type": "string",
                      "example": "http://terminology.hl7.org/CodeSystem/condition-clinical"
                    },
                    "code": { "type": "string", "example": "active" }
                  }
                }
              }
            }
          },
          "verificationStatus": {
            "type": "object",
            "properties": {
              "coding": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "system": {
                      "type": "string",
                      "example": "http://terminology.hl7.org/CodeSystem/condition-ver-status"
                    },
                    "code": { "type": "string", "example": "confirmed" }
                  }
                }
              }
            }
          },
          "code": {
            "type": "object",
            "properties": {
              "coding": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "system": { "type": "string", "example": "https://ndhm.gov.in/fhir/CodeSystem/namc" },
                    "code": { "type": "string", "example": "AB" },
                    "display": { "type": "string", "example": "Jaundice" }
                  }
                }
              },
              "text": { "type": "string", "example": "Jaundice" }
            }
          },
          "subject": {
            "type": "object",
            "properties": {
              "reference": { "type": "string", "example": "Patient/123456" },
              "identifier": {
                "type": "object",
                "properties": {
                  "system": { "type": "string", "example": "http://abdm.gov.in/ABHA" },
                  "value": { "type": "string", "example": "123456" }
                }
              }
            }
          },
          "onsetDateTime": {
            "type": "string",
            "format": "date",
            "example": "2025-09-10"
          },
          "recordedDate": {
            "type": "string",
            "format": "date-time",
            "example": "2025-09-10T06:48:00+05:30"
          },
          "recorder": {
            "type": "object",
            "properties": {
              "reference": { "type": "string", "example": "Practitioner/12345" },
              "display": { "type": "string", "example": "Dr. Smith" }
            }
          }
        }
      },
      "OperationOutcome": {
        "type": "object",
        "properties": {
          "resourceType": { "type": "string", "example": "OperationOutcome" },
          "issue": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "severity": { "type": "string" },
                "code": { "type": "string" },
                "details": { "type": "object" }
              }
            }
          }
        }
      },
    }
  }
}

    return jsonify(swagger_data)



@app.route("/")
def home():
    return render_template("index.html")

# For Displaying NAMASTE suggestions in the index page
@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    with open("Data/SiddhaJson.json", encoding="utf-8") as file:
        data = json.load(file)
        suggestions = [[item.get("code"), item.get("display"), item.get("designation")[0].get(
            "value")] for item in data.get("concept") if item.get("code").lower().startswith(query)]
        suggestions = suggestions[:20]
    return jsonify(suggestions)



# For Displaying NAMASTE suggestions in the Swagger ui page
@app.route('/api/suggestions/post', methods=['POST'])
def get_suggestions_via_post():
    query = request.get_json() or {}
    if "code" not in query or "coding" not in query["code"]:
        return jsonify({"error": "Missing code.coding in body"}), 400
    namc_code = query["code"]["coding"][0].get("code", "").lower()
    with open("Data/SiddhaJson.json", encoding="utf-8") as file:
        data = json.load(file)
        suggestions = [
            {"code": item.get("code"), "display": item.get("display"),
             "designation": item.get("designation")[0].get("value")}
            for item in data.get("concept", [])
            if item.get("code", "").lower().startswith(namc_code)
        ][:20]
    return jsonify(suggestions)


# For converting the given NAMC Code into the ICD-11 Codes in index page
@app.route("/api/submit", methods=["POST"])
def submit_term():
    request_data = request.get_json()
    items = request_data.get("term", "").split(",")
    english_term = items[1].strip()

    data = getICDDetailsFromEnglishDefinition(english_term, items[0])

    result_summary = f"Found {len(data)} result(s)"
    if data:
        result_summary += f" (e.g., '{data[0][0]}')"
    log_search_activity(f"'{english_term}'", result_summary)

    return jsonify(data)



# For converting the given NAMC Code into the ICD-11 Codes in SwaggerUI page
@app.route('/api/convert/post', methods=['POST'])
def convert():
    query = request.get_json() or {}
    if "code" not in query or "coding" not in query["code"]:
        return jsonify({"error": "Missing code.coding in body"}), 400
    namc_code = query["code"]["coding"][0].get("code", "").lower()

    definition = ""
    with open("Data/SiddhaJson.json", encoding="utf-8") as file:
        siddha_data = json.load(file)
        for item in siddha_data.get("concept", []):
            if item.get("code", "").lower() == namc_code:
                definition = item.get("display", "")
                break

    data = []
    if definition:
        search_term_info = f"{namc_code} -> '{definition}'"
        data = getICDDetailsFromEnglishDefinition(definition, namc_code)
        result_summary = f"Found {len(data)} result(s)"
        if data:
            result_summary += f" (e.g., '{data[0][0]}')"
        log_search_activity(search_term_info, result_summary)
    else:
        log_search_activity(f"'{namc_code}'", "Failed: No definition found")

    return jsonify(data)



# This is for returning the json from the index page and storing it in the database. This is called from the return button in the index page.
@app.route("/api/returnJson", methods=["POST"])
def returnJson():
    data = request.get_json()
    icd = data.get("icd")
    namc = data.get("namc")
    namc_code = namc.split(',')[0]
    icd_code = icd.split(',')[0]

    json_str = f'''{{
      "resourceType": "Condition",
      "id": "cond-123",
      "meta": {{ "...": "..." }},
      "code": {{
        "coding": [
          {{
            "system": "https://ndhm.gov.in/fhir/CodeSystem/namc",
            "code": "{namc_code}",
            "display": "{namc.split(',')[1].strip()}"
          }},
          {{
            "system": "http://id.who.int/icd11/mms",
            "code": "{icd_code}",
            "display": "{icd.split(',')[1].strip()}"
          }}
        ]
      }},
      "subject": {{ "...": "..." }}
    }}'''

    activity_description = f"FHIR Resource Generated (NAMC: {namc_code}, ICD: {icd_code})"
    log_search_activity(activity_description, f"\n{json_str}")

    return jsonify({"message": "Success, JSON logged."})


#NOTE: This is used when calling who icd ECT tool. It requires tokens so it is used to provide it.
@app.route("/api/newToken")
def newToken():

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
    return jsonify({"token" : token})



#NOTE: This is called for converting ICD to NAMC. The english term from the ECT tool is passed here
@app.route("/api/ICDtoNAMC")
def ICDtoNAMC():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Query parameter 'q' is missing."}), 400

    # Split and strip whitespace to get a clean search term
    try:
        term = query.split(",")[1].strip()
    except IndexError:
        # Handle cases where the input doesn't contain a comma
        term = query.strip()

    # The 'findNAMCTerm' function now returns a list of dicts with code and term
    matches = findNAMCTerm(term)

    # The matches are already in the correct format, so just return them
    return jsonify(matches)




if __name__ == "__main__":
    app.run(debug=True)
