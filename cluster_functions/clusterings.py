import pandas as pd
import numpy as np
from hdbscan import HDBSCAN
import nltk
from nltk.corpus import stopwords
import re
from categorization import load_transformers
from VARIABLE import CLUSTER_KEYWORDS, CONSINE_THRESHOLD
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn.functional as F

'''
Clustering with BERTopic
'''
def bertopic_clustering(embeddings, issues):
    tokenizer, model = load_transformers()
    print("Getting the cluster keywords position in multidimensional vector...")

    cluster_embeddings = {}

    for label, keywords in CLUSTER_KEYWORDS.items():
        inputs = tokenizer(
            keywords,
            padding="max_length",
            truncation=True,
            max_length=4096,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = model(**inputs)
        embed_cluster = outputs.last_hidden_state.mean(dim=1)
        cluster_embeddings[label] = embed_cluster.mean(dim=0)
    
    assigned_cluster = []
    for issue_vec in embeddings:
        issue_vec = issue_vec.unsqueeze(0) if len(issue_vec.shape) == 1 else issue_vec

        similarities = {}
        for cluster, cluster_vec in cluster_embeddings.items():
            cluster_vec = cluster_vec.unsqueeze(0) if len(cluster_vec.shape) == 1 else cluster_vec
            similarity = F.cosine_similarity(issue_vec, cluster_vec).item()
            similarities[cluster] = similarity

        best_cluster = max(similarities, key=similarities.get)
        best_score = similarities[best_cluster]
        assigned_cluster.append(best_cluster if best_score >= CONSINE_THRESHOLD else "outlier")
    grouping = {
        "register/login": [],
        "search": [],
        "permissions": [],
        "data issues": [],
        "notifications": [],
        "linked content": [],
        "outlier": []
    }
    for issue, label in zip(issues, assigned_cluster):
        grouping[label].append(issue)
    for label, issues in grouping.items():
        df = pd.DataFrame(issues, columns=["issue"])
        if label == "register/login":
            df.to_csv(f"../topic_split/register_issue.csv", index=False)
        else:
            df.to_csv(f"../topic_split/{label}_issue.csv", index=False)
    print("Clustering Finished...")

    



def main():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + '\n' + df["body"]).tolist()
    issue_numbers = df["url"].tolist()
    embed_df = pd.read_csv("../open_issue_embeddings.csv")
    embeds = embed_df.drop(columns=["texts"])
    df_numeric = embeds.apply(pd.to_numeric, errors='coerce')

    embeddings = torch.tensor(df_numeric.to_numpy(), dtype=torch.float32)
    
    # clusters = perform_clustering(15, embeddings, issues)
    bertopic_clustering(embeddings, issues)
    # df = pd.DataFrame({
    #     "issue": issues,
    #     "issue_link": issue_numbers,
    #     "topic": topics,
    #     "confidence_score": [str(p) for p in conf_score]
    # })
    # print("Clustering Finished...")
    # df.to_csv("../BERT_TOPIC_CLUSTER.csv", index=False)
    # topic_info.to_excel("../topic_info.xlsx", index=False)

if __name__ == "__main__":
    main()