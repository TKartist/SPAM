import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from transformers import LongformerTokenizer, LongformerModel
import torch
import pandas as pd
import os
from VARIABLE import TRANSFORMER_DIRECTORY, TRANSFORMER_DNAME


def load_transformers():
    print("Adding model and transformers...")
    dirs = os.listdir("../")
    model_name = "allenai/longformer-base-4096"

    if TRANSFORMER_DNAME in dirs:
        tokenizer = LongformerTokenizer.from_pretrained(TRANSFORMER_DIRECTORY)
        model = LongformerModel.from_pretrained(TRANSFORMER_DIRECTORY)
    else:
        os.makedirs(TRANSFORMER_DIRECTORY, exists_ok=True)
        tokenizer = LongformerTokenizer.from_pretrained(model_name)
        model = LongformerModel.from_pretrained(model_name)
        tokenizer.save_pretrained(TRANSFORMER_DIRECTORY)
        model.save_pretrained(TRANSFORMER_DIRECTORY)

    return tokenizer, model


def categorize_issues(issues):
    print("Performing the embedding...")

    tokenizer, model = load_transformers()
    inputs = tokenizer(issues, padding=True, truncation=True, max_length=4096, return_tensors="pt")
    device = "cuda" if torch.cuda.is_availabe() else "cpu"
    model = model.to(device)

    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
    
    embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    print(f"Embedding Shape: {embeddings.shape} \n")

    return embeddings


def perform_clustering(cluster_count, embeddings, issues):
    print("Performing K-means clustering...")
    kmeans = KMeans(n_clusters=cluster_count, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    s = ""
    for i, (text, cluster) in enumerate(zip(issues, clusters)):
        s += f"🔹 Issue {i+1}: Cluster {cluster}\n  → {text[:100]}...\n"
    with open("../cluster.txt", "w") as f:
        f.write(s)
    f.close()
    print("clusters saved in cluster.txt")
    return clusters


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


def main():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + '\n' + df["body"]).tolist()

    load_transformers()
    embeddings = categorize_issues(issues)
    clusters = perform_clustering(5, embeddings, issues)
    visualize_cluster(embeddings, clusters, issues)
    print("Completed the visualization")


if __name__ == "__main__":
    print("Running...")
    main()