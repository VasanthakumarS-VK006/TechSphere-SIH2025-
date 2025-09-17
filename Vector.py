# pip install sentence-transformers scikit-learn
import json
from sentence_transformers import SentenceTransformer, util

# 1. Load model
model = SentenceTransformer('all-MiniLM-L6-v2')



terms = {}
with open("SiddhaJson.json", encoding="utf-8") as file:
    data = json.load(file)

    for item in data.get("concept"):
        terms[item.get("code")] = item.get("definition")


definitions = list(terms.values())
    
embeddings = model.encode(definitions, convert_to_tensor=True)

# 4. Search function
def search(query, top_k=3):
    # Encode the query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.cos_sim(query_embedding, embeddings)[0]

    # Get top_k most similar terms
    top_results = similarities.topk(top_k)

    print(f"\nSearch: {query}\nResults:")
    for idx in top_results.indices:
        term = list(terms.keys())[idx]
        definition = definitions[idx]
        score = similarities[idx].item()
        print(f" - {term} (score={score:.3f}) → {definition}")

# 5. Try searching
search("wild animals")
search("Italian food")
search("vehicles for transport")


