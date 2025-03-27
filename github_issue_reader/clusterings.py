from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from bertopic import BERTopic
import numpy as np
from hdbscan import HDBSCAN
import re
from collections import Counter


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
    scan_model = HDBSCAN(min_cluster_size=5, min_samples=2, metric='euclidean')

    topic_model = BERTopic(hdbscan_model=scan_model, language="english")
    topics, conf_score = topic_model.fit_transform(issues, embeddings)

    topic_info = topic_model.get_topic_info()
    print(topic_info) 
    fig = topic_model.visualize_topics()
    top_words = topic_model.visualize_barchart(top_n_topics=10)
    topic_keywords = {
        topic: [word for word, _ in topic_model.get_topic(topic)]
        for topic in topic_model.get_topics()
        if topic != -1
    }

    # Convert to DataFrame
    df_topics = pd.DataFrame.from_dict(topic_keywords, orient="index")
    df_topics.to_csv("../bertopic_top_words.csv", index_label="topic")
    top_words.write_html("../topics_words_visual.html")
    fig.write_html("../topics_visual.html")
    return topics, conf_score




def main():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + '\n' + df["body"]).tolist()
    embed_df = pd.read_csv("../open_issue_embeddings.csv")
    embeds = embed_df.drop(columns=["texts"])
    df_numeric = embeds.apply(pd.to_numeric, errors='coerce')

    embeddings = df_numeric.to_numpy()
    # clusters = perform_clustering(15, embeddings, issues)
    topics, conf_score = bertopic_clustering(embeddings, issues)
    df = pd.DataFrame({
        "issue": issues,
        "topic": topics,
        "confidence_score" : conf_score
    })
    print("Clustering Finished...")
    df.to_csv("../BERT_TOPIC_CLUSTER.csv", index=False)

main()