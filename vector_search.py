from sentence_transformers import SentenceTransformer
from pymongo import MongoClient


client = MongoClient("mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/")
db = client["RecommendationSystemDB"]
papers_collection = db["Data"]

model = SentenceTransformer("all-mpnet-base-v2")
query_text = "deep learning for medical image analysis"

# Encode query
query_embedding = model.encode(query_text, convert_to_numpy=True).tolist()

# $search stage with knnBeta
pipeline = [
    {
        "$search": {
            "knnBeta": {
                "vector": query_embedding,
                "path": "embedding",
                "k": 5
            }
        }
    },
    {
        "$project": {
            "title": 1,
            "abstract": 1,
            "pdf_url": 1,
            "score": {"$meta": "searchScore"}
        }
    }
]

results = list(papers_collection.aggregate(pipeline))

for r in results:
    print(f"Score: {r.get('score', 0):.3f} | Title: {r.get('title', 'No Title')}")
    print(f"Link: {r.get('pdf_url', 'No PDF link available')}")

