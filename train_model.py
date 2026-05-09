import pandas as pd
import numpy as np
import re
import string
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download stopwords if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove @user handles
    text = re.sub(r'@[\w]*', '', text)
    # Remove special characters, numbers, punctuations
    text = re.sub(r'[^a-zA-Z#]', ' ', text)
    # Remove short words
    text = ' '.join([w for w in text.split() if len(w) > 3])
    
    # Tokenization and Stemming
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    tokens = text.split()
    stemmed_tokens = [stemmer.stem(w) for w in tokens if w not in stop_words]
    
    return ' '.join(stemmed_tokens)

print("Loading data...")
df = pd.read_csv('twitter.csv')

print("Cleaning tweets...")
df['tidy_tweet'] = df['tweet'].apply(clean_text)

print("Vectorizing data...")
tfidf_vectorizer = TfidfVectorizer(max_df=0.90, min_df=2, max_features=5000, stop_words='english', ngram_range=(1, 2))
tfidf = tfidf_vectorizer.fit_transform(df['tidy_tweet'])

print("Splitting data...")
train_tfidf = tfidf
X_train, X_test, y_train, y_test = train_test_split(train_tfidf, df['label'], random_state=42, test_size=0.2)

print("Training model...")
# Using class_weight='balanced' might help with precision/recall but can sometimes lower overall accuracy.
# Let's try without it first but with more features.
model = LogisticRegression(C=2.0, max_iter=1000)
model.fit(X_train, y_train)

print("Evaluating model...")
prediction = model.predict(X_test)
accuracy = accuracy_score(y_test, prediction)
print(f"Accuracy Score: {accuracy * 100:.2f}%")
print(classification_report(y_test, prediction))

if accuracy < 0.951:
    print("Accuracy still near 95%, trying Random Forest or XGBoost if available...")
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    accuracy = accuracy_score(y_test, prediction)
    print(f"Random Forest Accuracy Score: {accuracy * 100:.2f}%")

print("Saving model and vectorizer...")
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf_vectorizer, f)

print("Done!")
