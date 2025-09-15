from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from extraFunctions import getICDDetailsFromEnglishDefinition, getICDDetailsFromSiddhaDefinition, verifyABHAToken
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


# For Swagger
@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory('static', path)


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
    with open("Data/SiddhaJson.json") as file:
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
    with open("Data/SiddhaJson.json") as file:
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
      "meta": {{ ... }},
      "code": {{
        "coding": [
          {{
            "system": "https://ndhm.gov.in/fhir/CodeSystem/namc",
            "code": "{namc_code}",
            "display": "{namc.split(',')[1]}"
          }},
          {{
            "system": "http://id.who.int/icd11/mms",
            "code": "{icd_code}",
            "display": "{icd.split(',')[1]}"
          }}
        ]
      }},
      "subject": {{ ... }}
    }}'''  # Truncated for brevity

    activity_description = f"FHIR Resource Generated (NAMC: {namc_code}, ICD: {
        icd_code})"
    log_search_activity(activity_description, f"\n{json_str}")

    return jsonify({"message": "Success, JSON logged."})


# This is used when calling who icd ECT tool. It requires tokens so it is used to provide it.
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
    print("hello")
    print(token)
    return jsonify({"token" : token})

if __name__ == "__main__":
    app.run(debug=True)
