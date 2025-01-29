import re
import ast
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



# method 1 : using vader sentiment analysis tool to analyze the sentiment of the reviews

def darth_vader_storm_trooper_review():
    with open("output.txt", "r") as f:
        stringData = f.readlines()
        data = [ast.literal_eval(line.strip()) for line in stringData]
    analyzer = SentimentIntensityAnalyzer()
    for d in data:
        inquiry = d[-1]["subject"] + "\n" + d[-1]["body"]
        sentiment = analyzer.polarity_scores(inquiry)
        if sentiment["compound"] >= 0.05:
            print("Positive")
        else:
            print("Negative")
        print(sentiment)
        print(d[-1]["subject"])
        print("\n")

darth_vader_storm_trooper_review()