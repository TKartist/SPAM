import re
import ast
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')


def load_emails():
    with open("output.txt", "r") as f:
        stringData = f.read()
        data = ast.literal_eval(stringData)

    # for i in range(10):
    #     print("*" * 30)
    #     print(data[i]["subject"])
    #     print("*" * 30)
    #     print(data[i]["from"])
    #     print(data[i]["receivedDateTime"])
    #     print(data[i]["body"])
    #     print(data[i]["conversationID"])
    #     print("=" * 30)
    #     print("\n\n")
    

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
    custom_stopwords = {"hi", "hello", "your", "kind", "colleagues", "friends"}
    stop_words.update(custom_stopwords)

    tokens = [word for word in tokens if word not in stop_words]

    # We are going to use lemmatization instead of stemming
    # to be specific stemming means we are going to cut the words and remove suffixes i.e. improving, improved, improvement -> improv
    # lemmatization is going to convert the words to their base form i.e. improving, improved, improvement -> improve
    # lemmatization is more accurate but slower

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens 

# Example usage
# reviews = ["I love this platform! It's amazing.", "The service was terrible and slow.", "YoU CoulD DO SOOO MUCH BETTER!"]
# preprocessed_reviews = [preprocess_review(review) for review in reviews]
# print(preprocessed_reviews)

