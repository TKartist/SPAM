import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from VARIABLE import CLUSTER_KEYWORDS, CONSINE_THRESHOLD

def tf_idf_clustering(issues, issue_ids):
    for label, keywords in CLUSTER_KEYWORDS.items():
        query = " ".join(keywords)
        vectorizer = TfidfVectorizer()
        doc_vector = vectorizer.fit_transform([query] + issues)
        cosine_similarities = cosine_similarity(doc_vector[0:1], doc_vector[1:]).flatten()

        results = pd.DataFrame({
            "ids" : issue_ids,
            "issue": issues,
            "similarity": cosine_similarities
        })
        results = results[results["similarity"] >= CONSINE_THRESHOLD]
        print(len(results))
        results = results.sort_values(by="similarity", ascending=False)
        if label == "register/login":
            results.to_csv(f"../topic_split/register_login.csv", index=False)
        else:
            results.to_csv(f"../topic_split/{label}.csv", index=False)


df = pd.read_csv("../issues_folder/open_issues.csv")
df.fillna("", inplace=True)
issues = (df["title"] + df["body"]).tolist()
issue_ids = df["id"].tolist()
tf_idf_clustering(issues, issue_ids)
print("TF-IDF Clustering Finished...")