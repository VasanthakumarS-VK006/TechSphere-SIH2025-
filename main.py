from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from extraFunctions import getICDDetailsFromEnglishDefinition, getICDDetailsFromSiddhaDefinition
import json


app = Flask(__name__)


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


@app.route("/api/submit", methods=["POST"])
def submit_term():
    request_data = request.get_json()
    items = request_data.get("term", "").split(",")

    print(items[2])
    data = getICDDetailsFromEnglishDefinition(items[1])
    getICDDetailsFromSiddhaDefinition(items[2])

    # res = {"code": "AB",
    #        "english_term": "Jaundice",
    #        "ICD-11": "ME20.1"}

    return jsonify(data)


if __name__ == "__main__":

    with app.app_context():
        app.run(debug=True)
