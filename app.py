from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import uvicorn

# Download VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and vectorizer
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Text cleaning function (must match the one used during training)
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

class TweetRequest(BaseModel):
    tweet: str

@app.get("/")
def read_root():
    return {"message": "Twitter Sentiment Analysis API"}

@app.post("/predict")
def predict_sentiment(request: TweetRequest):
    try:
        cleaned = clean_text(request.tweet)
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
            # Model predicts it's not hate. Use VADER to see if it's positive or neutral
            scores = sia.polarity_scores(request.tweet)
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
                
        return {
            "prediction": status_code,
            "label": label,
            "confidence": confidence,
            "cleaned_tweet": cleaned
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
