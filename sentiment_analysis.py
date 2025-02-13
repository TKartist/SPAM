import re
import ast
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')    

# method 2: using nltk to preprocess the reviews and then analyze the sentiment through machine learning OR deep learning models


# removing common phrases in emails which could skew the analysis
def remove_email_phrases(text):
    phrases = ["dear", "best regards", "sincerely", "kind regards", "warm regards", "thank you", "thanks", "please"]
    for phrase in phrases:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)
    return text

def preprocess_review(text):
    text = text.lower() # convert to lowercase first ALWAYS
    text = re.sub(r'[^\w\s]', '', text) # remove punctuation
    text = remove_email_phrases(text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))

    # some stop words in emails
    custom_stopwords = {"hi", "hello", "email", "address", 
                        "ifrc", "your", "kind", "colleagues", 
                        "friends", "unless", }
    stop_words.update(custom_stopwords)

    tokens = [word for word in tokens if word not in stop_words]

    # We are going to use lemmatization instead of stemming
    # to be specific stemming means we are going to cut the words and remove suffixes i.e. improving, improved, improvement -> improv
    # lemmatization is going to convert the words to their base form i.e. improving, improved, improvement -> improve
    # lemmatization is more accurate but slower

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def overall_words_used():
    with open("output.txt", "r") as f:
        stringData = f.readlines()
        data = [ast.literal_eval(line.strip()) for line in stringData]
        all_words = []
        for d in data:
            all_words += preprocess_review(d[-1]["subject"] + " " + d[-1]["body"])
        word_freq = Counter(all_words)
        for word in word_freq.most_common(len(data) * 3):
            print(word)

# Example usage
# reviews = ["I love this platform! It's amazing.", "The service was terrible and slow.", "YoU CoulD DO SOOO MUCH BETTER!"]
# preprocessed_reviews = [preprocess_review(review) for review in reviews]
# print(preprocessed_reviews)

overall_words_used()

