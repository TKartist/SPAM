import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from VARIABLE import CLUSTER_KEYWORDS, CONSINE_THRESHOLD
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string



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


def perform_clustering():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + df["body"]).tolist()
    df["url"] = df["url"].apply(lambda x: x.split("/")[-1])
    issue_ids = df["url"].tolist()
    tf_idf_clustering(issues, issue_ids)
    print("TF-IDF Clustering Finished...")


def analyze_clusters():
    category_files = os.listdir("../topic_split")
    category_analysis = {
        "category" : [],
        "issue_count" : [],
        "similarity_avg" : [],
        "max_similarity" : [],
        "top_words" : []
    }
    
    stopword = set(stopwords.words('english'))
    stopword.update(string.punctuation)
    stopword.update(["\n", "\r", "\t"])
    
    custom_stopwords = {"issues", "issue", "ifrc", "go", "ifrcgo", "ifrc-go", ".org", ".com", "https", "www", "x"}
    stopword.update(custom_stopwords)

    for file in category_files:
        if file.endswith(".csv"):
            df = pd.read_csv(f"../topic_split/{file}")
            print(f"File: {file}, Number of Issues: {len(df)}")

            text = " ".join(df["issue"].tolist())
            text = text.lower()
            tokens = word_tokenize(text)
            filtered_tokens = [word for word in tokens if word.isalpha() and word not in stopword]
            word_counts = Counter(filtered_tokens)
            most_common_words = word_counts.most_common(10)
            common_string = " ".join([f"{word}({count})" for word, count in most_common_words])
            category_analysis["category"].append(file.split(".")[0])
            category_analysis["issue_count"].append(len(df))
            category_analysis["similarity_avg"].append(df["similarity"].mean())
            category_analysis["max_similarity"].append(df["similarity"].max())
            category_analysis["top_words"].append(common_string)
        else:
            continue
    result_df = pd.DataFrame(category_analysis)
    result_df.to_csv("../cluster_analysis.csv", index=False)
    print("Cluster Analysis Finished...")
    print(result_df.head())

perform_clustering()
analyze_clusters()