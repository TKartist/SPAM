import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from transformers import LongformerTokenizer, LongformerModel
import torch

def categorize_issues(issues):
    model_name = "allenai/longformer-base-4096"
    tokenizer = LongformerTokenizer(model_name)
    model = LongformerModel.from_pretrained(model_name)

    inputs = tokenizer(issues, padding=True, truncation=True, max_length=4096, return_tensors="pt")
    device = "cuda" if torch.cuda.is_availabe() else "cpu"
    model = model.to(device)

    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
    
    embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    print(f"Embedding Shape: {embeddings.shape}")

    return embeddings


def perform_clustering(cluster_count, cluster_issues, issues):
    kmeans = KMeans(n_clusters=cluster_count, random_state=42)
    clusters = kmeans.fit_predict(cluster_issues)

    for i, (text, cluster) in enumerate(zip(issues, clusters)):
        f"🔹 Issue {i+1}: Cluster {cluster}\n  → {text[:100]}...\n"
    return clusters


def visualize_cluster():
    print("dam")


