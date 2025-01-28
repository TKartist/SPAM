import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_review(text):
    text = text.lower() # convert to lowercase first ALWAYS
    text = re.sub(r'[^\w\s]', '', text) # remove punctuation
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
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

