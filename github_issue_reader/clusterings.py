from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from bertopic import BERTopic
import numpy as np
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
import re
from collections import Counter
import umap.umap_ as umap_
import umap

nltk.download('stopwords')
stopwords = stopwords.words('english')

def visualize_cluster(embeddings, clusters, issues):
    print("Plotting the clusters...")
    tsne = TSNE(n_components=2, random_state=42)
    reduced_embeddings = tsne.fit_transform(embeddings)
    plt.figure(figsize=(10, 7))
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=clusters, cmap="viridis", alpha=0.7)
    for i, txt in enumerate(range(len(issues))):
        plt.annotate(txt, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]), fontsize=9)
    plt.title("Longformer-Based GitHub Issue Clustering")
    plt.savefig("issue_analysis.png")


def perform_clustering(cluster_count, embeddings, issues):
    print("Performing K-means clustering...")
    kmeans = KMeans(n_clusters=cluster_count, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    s = ""
    box = []
    for i, (text, cluster) in enumerate(zip(issues, clusters)):
        box.append({
            "index" : i,
            "cluster" : cluster,
            "text" : text
        })
    df = pd.DataFrame(box)
    df.sort_values(by="cluster", inplace=True)
    df.to_csv("../cluster_organization.csv", index=False)
    print("clusters saved in cluster.txt")
    print(clusters)
    return clusters


'''
Clustering with BERTopic
'''
def bertopic_clustering(embeddings, issues):
    print("Performing BERTopic clustering...")
    scan_model = HDBSCAN(min_cluster_size=2, min_samples=2, metric='euclidean', cluster_selection_method='eom',prediction_data=True)

    custom_stopwords = stopwords + ["https", "com", "www", "org", "http", "github", "issue", "issues", "ifrc", "open", "closed", "opened", "ifrcgo", "x"]
    vectorizer_model = CountVectorizer(stop_words=custom_stopwords, ngram_range=(1, 2),min_df=2)
    
    # UMAP (helps reduce embedding noise and improve clustering)
    umap_model = umap_.UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric='cosine'
    )

    topic_model = BERTopic(hdbscan_model=scan_model, umap_model=umap_model, vectorizer_model=vectorizer_model, calculate_probabilities=True, verbose=True)
    topics, prob = topic_model.fit_transform(issues, embeddings)

    topic_info = topic_model.get_topic_info()
    print(topic_info) 
    return topics, prob, topic_info




def main():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + '\n' + df["body"]).tolist()
    issue_numbers = df["url"].tolist()
    embed_df = pd.read_csv("../open_issue_embeddings.csv")
    embeds = embed_df.drop(columns=["texts"])
    df_numeric = embeds.apply(pd.to_numeric, errors='coerce')

    embeddings = df_numeric.to_numpy()
    # clusters = perform_clustering(15, embeddings, issues)
    topics, conf_score, topic_info = bertopic_clustering(embeddings, issues)
    df = pd.DataFrame({
        "issue": issues,
        "issue_link": issue_numbers,
        "topic": topics,
        "confidence_score": [str(p) for p in conf_score]
    })
    print("Clustering Finished...")
    df.to_csv("../BERT_TOPIC_CLUSTER.csv", index=False)
    topic_info.to_excel("../topic_info.xlsx", index=False)

if __name__ == "__main__":
    main()