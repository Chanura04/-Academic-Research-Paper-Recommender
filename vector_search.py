from sentence_transformers import SentenceTransformer
from pymongo import MongoClient


class VectorSearch:
    def __init__(self,query_text):
        self.query_text = query_text
        self.client = MongoClient("mongodb+srv://Chanura04:chanura2004@academicresearchpaperre.fibwqgy.mongodb.net/")
        self.db = self.client["RecommendationSystemDB"]
        self.papers_collection = self.db["Data"]
        self.model = SentenceTransformer("all-mpnet-base-v2")




    def encode_query(self):
        query_embedding = self.model.encode(self.query_text, convert_to_numpy=True).tolist()

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
        results = list(self.papers_collection.aggregate(pipeline))
        return self.search(results)

    def search(self,results):
        for r in results:
            print(f"Score: {r.get('score', 0):.3f} | Title: {r.get('title', 'No Title')}")
            print(f"Link: {r.get('pdf_url', 'No PDF link available')}")
        return results





# a=VectorSearch("machine learning")
# a.show()



#
# import random
# id=random.randint(0,9999)
#
# username=['a','f','s','e']
# chr=random.choice(username)
# print(f"{id}{chr}")


# for r in results:
#     print(f"Score: {r.get('score', 0):.3f} | Title: {r.get('title', 'No Title')}")
#     print(f"Link: {r.get('pdf_url', 'No PDF link available')}")

