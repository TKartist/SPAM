import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from VARIABLE import CLUSTER_KEYWORDS, CONSINE_THRESHOLD
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
import ast
from analyze_emails import collect_root_emails
import spacy
import re
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))
stop_words.update(string.punctuation)
stop_words.update(["\n", "\r", "\t"])
stop_words.update({"ifrc", "red", "cross", "go", "ifrcgo", "ifrc-go", ".org", ".com", "https", "www", "x", "best regards", "kind regards", "regards", "sincerely", "thank you", "thanks", "cheers", "best", "warm regards", "warmest regards", "yours sincerely", "yours faithfully", "yours truly", "respectfully yours", "with appreciation", "with gratitude", "hello", "dear", "hi", "hey", "greetings", "to whom it may concern", "good morning", "good afternoon", "good evening", "thank you for your email", "thank you for reaching out", "thank you for contacting us", "thank you for your message", "colleagues", "team", "all", "everyone", "all the best", "take care", "best wishes", "wishing you well", "wishing you all the best", "wishing you success", "wishing you happiness", "wishing you joy", "wishing you peace", "wishing you prosperity", "wishing you good health", "wishing you a great day"})

similarities = {
    "email" : [],
    "github" : []
}

def read_output():
    with open("../output.txt", "r") as f:
        stringData = f.readlines()
        data = [ast.literal_eval(line.strip()) for line in stringData]
    return data


def lemma_keywords(keywords):
    cleaned_keywords = []
    for keyword in keywords:
        cleaned_keywords.append(nlp(keyword)[0].lemma_)
    return cleaned_keywords


def clean_email(issue):
    cleaned_text = issue.replace("[external email] do not click links or attachments unless you expect it from the sender, you check it came from a known email address and you know the content is safe.", "")
    cleaned_text = cleaned_text.replace("you don't often get email from", "")
    cleaned_text = cleaned_text.replace("learn why this is important", "")
    return cleaned_text


def lemmatize_clean_text(issues):
    cleaned_issues = []
    for issue in issues:
        cleaned_text = clean_email(issue)

        tokens = word_tokenize(cleaned_text)
        filtered = [word for word in tokens if word.isalnum() and word not in stop_words]
        cleaned_issues.append(" ".join(filtered))
    return [" ".join([t.lemma_ for t in nlp(text)]) for text in cleaned_issues]


def plot_similarity_distribution(df, category, tag):
    plt.figure(figsize=(10, 6))
    plt.hist(df["similarity"], bins=30, color='blue', alpha=0.7)
    plt.title(f"Similarity Distribution for {category}")
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Frequency")
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f"../similarity_distribution_{category}.png")
    plt.close()


def tf_idf_clustering(original, issues, issue_ids, tag):
    vectorizer = CountVectorizer()
    doc_vector = vectorizer.fit_transform(issues)
    for label, keywords in CLUSTER_KEYWORDS.items():
        keys = lemma_keywords(keywords)
        query = " ".join(keys)
        query_vector = vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, doc_vector).flatten()

        results = pd.DataFrame({
            "ids" : issue_ids,
            "issue": original,
            "similarity": cosine_similarities
        })
        if tag == "github":
            back = results[results["similarity"] <= 0.104]
            back.to_csv(f"../irrelevant_split/other_{label}_{tag}.csv", index=False)
            results = results[results["similarity"] >= CONSINE_THRESHOLD]
            similarities["github"] += cosine_similarities.tolist()
        else:
            back = results[results["similarity"] <= 0.104]
            back.to_csv(f"../irrelevant_split/other_{label}_{tag}.csv", index=False)
            results = results[results["similarity"] >= 0.105]
            similarities["email"] += cosine_similarities.tolist()
        results = results.sort_values(by="similarity", ascending=False)
        if label == "register/login":
            results.to_csv(f"../topic_split/register_login_{tag}.csv", index=False)
        else:
            results.to_csv(f"../topic_split/{label}_{tag}.csv", index=False)


def perform_clustering():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + df["body"]).tolist()
    df["url"] = df["url"].apply(lambda x: x.split("/")[-1])
    issue_ids = df["url"].tolist()
    tf_idf_clustering(issues, issues, issue_ids, "github")
    print("TF-IDF Clustering GitHub Issues Finished...")


def perform_clustering_emails():
    print("Performing the clustering on emails...")
    email_issues = collect_root_emails()
    email_issues = [email.lower() for email in email_issues]
    cleaned_issues = lemmatize_clean_text(email_issues)

    ids = list(range(len(email_issues)))
    tf_idf_clustering(email_issues, cleaned_issues, ids, "email")
    print("TF-IDF Clustering Email Issues Finished...")


def plot_similarity_distribution(df, category):
    plt.figure(figsize=(15, 9))
    plt.scatter(range(len(df)), df["similarity"], alpha=0.6)
    plt.axhline(y=0.05, color='red', linestyle='--', label=f'Threshold = 0.05 {len(df[df["similarity"] >= 0.05])} docs')
    plt.axhline(y=0.07, color='yellow', linestyle='--', label=f'Threshold = 0.07 {len(df[df["similarity"] >= 0.07])} docs')
    plt.axhline(y=0.09, color='green', linestyle='--', label=f'Threshold = 0.09 {len(df[df["similarity"] >= 0.09])} docs')
    plt.axhline(y=0.105, color='blue', linestyle='--', label=f'Threshold = 0.105 {len(df[df["similarity"] >= 0.105])} docs')
    plt.axhline(y=0.3, color='black', linestyle='--', label=f'Threshold = 0.3 {len(df[df["similarity"] >= 0.3])} docs')
    
    plt.title(f"Cosine Similarity Distribution for {category} docs")
    plt.xlabel("Document Index")
    plt.ylabel("Cosine Similarity")
    plt.legend()
    plt.savefig(f"../similarity_distribution_{category}.png")
    plt.close()


def plot_doc_count(df, category):
    similarity_trhesholds = [round(i * 0.01, 2) for i in range(1, 51)]
    doc_count = []
    for threshold in similarity_trhesholds:
        doc_count.append(len(df[df["similarity"] >= threshold]))
    plt.figure(figsize=(15, 9))
    plt.plot(similarity_trhesholds, doc_count)
    plt.xlabel("Cosine Similarity Threshold")
    plt.ylabel("Document Count")
    plt.legend()
    plt.title(f"Document Count vs Cosine Similarity Threshold for {category} docs")
    plt.savefig(f"../similarity_threshold_{category}.png")
    plt.close()



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
            text = clean_email(text)
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



def generate_similarity_graph():
    df_email = pd.read_csv("../similarity_email.csv")
    df_github = pd.read_csv("../similarity_github.csv")

    plot_similarity_distribution(df_email, "email")
    plot_similarity_distribution(df_github, "github")
    plot_doc_count(df_email, "email")
    plot_doc_count(df_github, "github")
    print("Similarity Graph Generated...")