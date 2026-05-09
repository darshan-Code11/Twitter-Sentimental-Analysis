import sys
import json
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import warnings

# Suppress sklearn warnings to keep stdout clean for JSON parsing
warnings.filterwarnings("ignore")

# Load model and vectorizer
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Text cleaning function
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'@[\w]*', '', text)
    text = re.sub(r'[^a-zA-Z#]', ' ', text)
    text = ' '.join([w for w in text.split() if len(w) > 3])
    tokens = text.split()
    stemmed_tokens = [stemmer.stem(w) for w in tokens if w not in stop_words]
    return ' '.join(stemmed_tokens)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tweet = sys.argv[1]
        try:
            cleaned = clean_text(tweet)
            vec = vectorizer.transform([cleaned])
            prediction = model.predict(vec)[0]
            
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(vec)[0]
                confidence = float(max(probs))
            else:
                confidence = 1.0
                
            if prediction == 1:
                label = "Negative / Hate"
                status_code = -1
            else:
                scores = sia.polarity_scores(tweet)
                compound = scores['compound']
                if compound >= 0.05:
                    label = "Positive"
                    status_code = 1
                elif compound <= -0.05:
                    label = "Negative (Non-toxic)"
                    status_code = -1
                else:
                    label = "Neutral"
                    status_code = 0
                    
            result = {
                "prediction": status_code,
                "label": label,
                "confidence": confidence,
                "cleaned_tweet": cleaned
            }
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
    else:
        print(json.dumps({"error": "No tweet provided"}))
