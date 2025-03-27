import pandas as pd
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from collections import Counter


def understanding_clusters():
    df = pd.read_csv("../BERT_TOPIC_CLUSTER.csv")
    dfs_by_topic = {topic: group_df for topic, group_df in df.groupby("topic")}
    for topic, group_df in dfs_by_topic.items():
        group_df.to_csv(f"topic_{topic+1}.csv", index=False)
        issues = group_df["issue"].tolist()
        all_text = " ".join(issues).lower()

        new_words = ["https", "com", "www", "org", "http", "github", "issue", "issues", "ifrc", "open", "closed", "opened", "ifrcgo", "x"]
        custom_words = set(ENGLISH_STOP_WORDS)
        custom_words.update(new_words)
        words = re.findall(r'\b\w+\b', all_text)
        filtered_words = [word for word in words if word not in custom_words]
        word_freq = Counter(filtered_words)
        print(f"Top 10 words for topic {topic} is : {word_freq.most_common(10)}")
        print("=====================================================")

understanding_clusters()