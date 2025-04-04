import pandas as pd
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from collections import Counter
import string


def understanding_clusters():
    df = pd.read_csv("../BERT_TOPIC_CLUSTER.csv")
    dfs_by_topic = {topic: group_df for topic, group_df in df.groupby("topic")}
    for topic, group_df in dfs_by_topic.items():
        group_df = group_df[["issue", "topic"]]
        group_df.to_excel(f"../topic_split/topic_{topic+1}.xlsx", index=False)
        

understanding_clusters()