from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_oauthlib.provider import OAuth2Provider  # For OAuth 2.0 (prototype)
from extraFunctions import getICDDetailsFromEnglishDefinition, getICDDetailsFromSiddhaDefinition
import json
import datetime  # For timestamps/audits

app = Flask(__name__)
CORS(app)
oauth = OAuth2Provider(app)  # Prototype OAuth; integrate ABHA in production

# Load NAMC CodeSystem
with open("SiddhaJson.json") as file:
    namc_codesystem = json.load(file)

# Generate ValueSet for NAMC
namc_valueset = {
    "resourceType": "ValueSet",
    "id": "namc-vs",
    "url": "http://example.com/fhir/ValueSet/namc-vs",
    "name": "NAMCValueSet",
    "status": "active",
    "compose": {
        "include": [{"system": "https://ndhm.gov.in/fhir/CodeSystem/namc"}]
    }
}

# Prototype ConceptMap (add more mappings dynamically via API queries)
namc_to_icd11_conceptmap = {
    "resourceType": "ConceptMap",
    "id": "namc-to-icd11",
    "url": "http://example.com/fhir/ConceptMap/namc-to-icd11",
    "name": "NAMCToICD11Map",
    "status": "draft",
    "group": [{
        "source": "https://ndhm.gov.in/fhir/CodeSystem/namc",
        "target": "http://id.who.int/icd/release/11/mms",
        "element": [
            {  # Example for Jaundice
                "code": "AB",
                "display": "Jaundice",
                "target": [
                    {"code": "ME10.1", "display": "Unspecified jaundice", "equivalence": "equivalent"},  # Biomedicine
                    {"code": "SA01", "display": "Jaundice disorder (TM1)", "equivalence": "equivalent"}   # TM (fallback to TM1 until TM2 available)
                ]
            },
            {  # Example for Hepatic disease
                "code": "AA",
                "display": "Hepatic disease",
                "target": [
                    {"code": "DB99", "display": "Liver disease, unspecified", "equivalence": "equivalent"},  # Biomedicine
                    {"code": "SA00", "display": "Liver system disorders (TM1)", "equivalence": "equivalent"}  # TM
                ]
            }
            # Add more via dynamic queries in /api/submit
        ]
    }]
}

# In-memory store for bundles (prototype; use DB in production)
bundles = []

# Audit log (prototype)
audit_log = []

# OAuth dummy client (for ABHA simulation)
clients = {'client_id': {'client_secret': 'secret', 'redirect_uris': [], 'grant_types': ['authorization_code']}}

@oauth.clientgetter
def load_client(client_id):
    return clients.get(client_id)

@app.route("/")
def home():
    return render_template("index.html")  # Assume updated with search form and FHIR output

@app.route('/api/suggestions', methods=['GET'])  # FHIR-like $expand
def get_suggestions():
    query = request.args.get('filter', '').lower()  # Changed to 'filter' for FHIR $expand param
    if not query:
        return jsonify({"resourceType": "Parameters", "parameter": [{"name": "expansion", "resource": {"expansion": []}}]})

    concepts = namc_codesystem.get("concept", [])
    suggestions = []
    for item in concepts:
        code = item.get("code", "").lower()
        display = item.get("display", "").lower()
        designation = item.get("designation", [{}])[0].get("value", "").lower()
        if query in code or query in display or query in designation:
            suggestions.append([item.get("code"), item.get("display"), item.get("designation", [{}])[0].get("value")])

    # Return as FHIR expansion
    expansion = {"resourceType": "ValueSet", "expansion": {"contains": [{"system": namc_codesystem["url"], "code": s[0], "display": s[1]} for s in suggestions[:20]]}}
    return jsonify({"resourceType": "Parameters", "parameter": [{"name": "expansion", "resource": expansion}]})

@app.route("/api/submit", methods=["POST"])  # Dynamic mapping; extends to update ConceptMap
def submit_term():
    request_data = request.get_json()
    items = request_data.get("term", "").split(",")
    code, english_term, siddha_term = items[0], items[1], items[2]

    # Query ICD-11 for mappings (Biomedicine/TM)
    english_results = getICDDetailsFromEnglishDefinition(english_term)
    siddha_results = getICDDetailsFromSiddhaDefinition(siddha_term)

    # Prototype: Add to ConceptMap (in production, persist)
    new_element = {"code": code, "display": english_term, "target": []}
    for res in english_results + [r["code"] for r in siddha_results if "code" in r]:
        new_element["target"].append({"code": res[0], "display": res[1], "equivalence": "equivalent"})
    namc_to_icd11_conceptmap["group"][0]["element"].append(new_element)

    # Return candidates for UI selection
    return jsonify({"namc_code": code, "icd11_candidates": english_results + [[r["code"], r["title"]] for r in siddha_results]})

@app.route("/CodeSystem/namc", methods=["GET"])
def get_codesystem():
    namc_codesystem["meta"] = {"versionId": "1", "lastUpdated": datetime.datetime.now().isoformat()}  # Versioning
    return jsonify(namc_codesystem)

@app.route("/ValueSet/namc-vs", methods=["GET"])
def get_valueset():
    namc_valueset["meta"] = {"versionId": "1", "lastUpdated": datetime.datetime.now().isoformat()}
    return jsonify(namc_valueset)

@app.route("/ConceptMap/namc-to-icd11", methods=["GET"])
def get_conceptmap():
    namc_to_icd11_conceptmap["meta"] = {"versionId": "1", "lastUpdated": datetime.datetime.now().isoformat()}
    return jsonify(namc_to_icd11_conceptmap)

@app.route("/ConceptMap/$translate", methods=["POST"])  # FHIR $translate
@oauth.require_oauth()  # Secured
def translate():
    params = request.get_json()
    code = params.get("code")
    system = params.get("system")  # e.g., NAMC URL
    target_system = params.get("targetsystem")  # ICD-11 URL

    # Audit
    audit_log.append({"user": request.oauth.user, "action": "translate", "timestamp": datetime.datetime.now().isoformat(), "consent": params.get("meta", {}).get("security")})

    for group in namc_to_icd11_conceptmap["group"]:
        if group["source"] == system:
            for elem in group["element"]:
                if elem["code"] == code:
                    matches = [t for t in elem["target"] if target_system in t["code"]]  # Filter by target
                    return jsonify({"resourceType": "Parameters", "parameter": [{"name": "match", "valueCodeableConcept": {"coding": [{"system": target_system, "code": m["code"], "display": m["display"]}]}} for m in matches]})

    return jsonify({"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "not-found"}]}), 404

@app.route("/Bundle", methods=["POST"])  # Upload encounter with dual-coding
@oauth.require_oauth()
def upload_bundle():
    bundle = request.get_json()
    # Validate dual-coding (NAMC + ICD-11 in Condition.code)
    for entry in bundle.get("entry", []):
        resource = entry.get("resource")
        if resource.get("resourceType") == "Condition":
            codings = resource.get("code", {}).get("coding", [])
            has_namc = any(c.get("system") == namc_codesystem["url"] for c in codings)
            has_icd11 = any("id.who.int/icd/release/11" in c.get("system", "") for c in codings)
            if not (has_namc and has_icd11):
                return jsonify({"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "invalid", "details": {"text": "Missing dual-coding"}}]}), 400

    # Add metadata for consent/versioning
    bundle["meta"] = {"versionId": str(len(bundles) + 1), "lastUpdated": datetime.datetime.now().isoformat(), "security": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "CONSENT"}]}

    bundles.append(bundle)
    audit_log.append({"user": request.oauth.user, "action": "upload", "timestamp": datetime.datetime.now().isoformat(), "consent": bundle["meta"]["security"]})

    return jsonify(bundle), 201

@app.route("/audit", methods=["GET"])  # View audits (secured)
@oauth.require_oauth()
def get_audit():
    return jsonify(audit_log)

if __name__ == "__main__":
    app.run(debug=True)
