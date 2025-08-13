from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import numpy as np

# Connect to MongoDB
client = MongoClient("mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/")
db = client["RecommendationSystemDB"]
papers_collection = db["Data"]

# Load embedding model
model = SentenceTransformer("all-mpnet-base-v2")

# Fetch papers without embeddings
papers = list(papers_collection.find({"embedding": {"$exists": False}}))
i=0
for paper in papers:
    text = f"{paper['title']} {paper['abstract']}"
    embedding = model.encode(text, convert_to_numpy=True).tolist()

    # Store embedding in MongoDB
    papers_collection.update_one(
        {"_id": paper["_id"]},
        {"$set": {"embedding": embedding}}
    )
    i+=1
    print(f"Paper {i} updated with embedding.")

print(f"Updated {len(papers)} papers with embeddings.")
