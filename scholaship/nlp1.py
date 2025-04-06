import pandas as pd
import spacy
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import make_pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.nlp = nlp

    def preprocess_text(self, text):
        """Preprocess text by lowercasing, lemmatizing, and removing stopwords/punctuation."""
        doc = self.nlp(text.lower())
        processed_text = " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])
        return processed_text

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        """Apply preprocessing to a list of texts."""
        return [self.preprocess_text(text) for text in X]

def load_data(file_path):
    """Load the dataset and drop rows with missing eligibility text."""
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["Eligibility"])  # Drop rows with missing eligibility
    return df

def extract_numeric_conditions(user_input):
    """Extract numeric conditions like family income, age, marks, etc. from user input."""
    conditions = {}
    
    # Extract family income
    income_match = re.search(r"(income|salary).*?(\d+)\s*(lakh|lac)", user_input, re.IGNORECASE)
    if income_match:
        conditions["family_income"] = float(income_match.group(2))
    
    # Extract age
    age_match = re.search(r"(age).*?(\d+)", user_input, re.IGNORECASE)
    if age_match:
        conditions["age"] = int(age_match.group(2))
    
    # Extract marks
    marks_match = re.search(r"(marks|percentage).*?(\d+)", user_input, re.IGNORECASE)
    if marks_match:
        conditions["marks"] = int(marks_match.group(2))
    
    return conditions

def filter_scholarships(df, conditions):
    """Filter scholarships based on numeric conditions."""
    filtered_df = df.copy()
    
    # Filter by family income
    if "family_income" in conditions:
        filtered_df = filtered_df[filtered_df["Eligibility"].str.contains(r"income.*?\d+\s*(lakh|lac)", case=False, regex=True)]
        filtered_df = filtered_df[filtered_df["Eligibility"].apply(lambda x: float(re.search(r"(\d+)\s*(lakh|lac)", x).group(1)) <= conditions["family_income"])]
    
    # Filter by age
    if "age" in conditions:
        filtered_df = filtered_df[filtered_df["Eligibility"].str.contains(r"age.*?\d+", case=False, regex=True)]
        filtered_df = filtered_df[filtered_df["Eligibility"].apply(lambda x: int(re.search(r"age.*?(\d+)", x).group(1)) <= conditions["age"])]
    
    # Filter by marks
    if "marks" in conditions:
        filtered_df = filtered_df[filtered_df["Eligibility"].str.contains(r"marks.*?\d+", case=False, regex=True)]
        filtered_df = filtered_df[filtered_df["Eligibility"].apply(lambda x: int(re.search(r"marks.*?(\d+)", x).group(1)) >= conditions["marks"])]
    
    return filtered_df

def train_nlp_model(df):
    """Train the NLP pipeline (preprocessing + TF-IDF vectorization)."""
    preprocessor = TextPreprocessor()
    vectorizer = TfidfVectorizer(max_df=0.85, max_features=5000, ngram_range=(1, 2))
    pipeline = make_pipeline(preprocessor, vectorizer)
    tfidf_matrix = pipeline.fit_transform(df["Eligibility"])
    return pipeline, tfidf_matrix, df

def recommend_scholarships(user_input, pipeline, tfidf_matrix, df, top_n=3, threshold=0.1):
    """Recommend scholarships based on user input."""
    # Extract numeric conditions
    conditions = extract_numeric_conditions(user_input)
    
    # Filter scholarships based on conditions
    filtered_df = filter_scholarships(df, conditions)
    
    # If no scholarships match, return no match
    if len(filtered_df) == 0:
        return [{"Scholarship Name": "No match found", "Provider": "N/A", "Eligibility": "N/A", "Amount": "N/A", "Similarity Score": 0}]
    
    # Preprocess user input
    user_input_processed = pipeline.named_steps['textpreprocessor'].preprocess_text(user_input)
    user_tfidf = pipeline.named_steps['tfidfvectorizer'].transform([user_input_processed])

    # Compute similarity scores for filtered scholarships
    filtered_tfidf_matrix = pipeline.named_steps['tfidfvectorizer'].transform(filtered_df["Eligibility"])
    similarity_scores = cosine_similarity(user_tfidf, filtered_tfidf_matrix).flatten()

    # Get top matches
    top_indices = similarity_scores.argsort()[-top_n:][::-1]
    top_scores = similarity_scores[top_indices]

    recommendations = []
    for idx, score in zip(top_indices, top_scores):
        if score >= threshold:
            scholarship = filtered_df.iloc[idx][["Scholarship Name", "Provider", "Eligibility", "Amount"]].to_dict()
            for key, value in scholarship.items():
                if pd.isna(value):
                    scholarship[key] = None
            scholarship["Similarity Score"] = score
            recommendations.append(scholarship)

    return recommendations if recommendations else [{"Scholarship Name": "No match found", "Provider": "N/A", "Eligibility": "N/A", "Amount": "N/A", "Similarity Score": 0}]
