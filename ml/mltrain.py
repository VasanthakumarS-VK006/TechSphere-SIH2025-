# model_training_ml.py
# This script trains a machine learning model to classify the priority of civic issues.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import math
from tqdm import tqdm

# --- Configuration ---
DATA_FILE = "civic_issues_labeled.csv"
VECTORIZER_FILE = "vectorizer.joblib"
MODEL_FILE = "model.joblib"

def train_model():
    """Loads data, trains the model, and saves it."""
    # 1. Load the dataset with a progress bar
    print(f"Loading data from '{DATA_FILE}'...")
    try:
        # Get total number of lines to configure tqdm
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            # Subtract 1 for the header row
            total_lines = sum(1 for line in f) - 1

        chunk_size = 100  # Process 100 rows at a time
        
        # Calculate the number of chunks to process
        num_chunks = math.ceil(total_lines / chunk_size)
        
        chunks = []
        # Use pd.read_csv with chunksize and wrap the iterator with tqdm
        with tqdm(total=num_chunks, desc="Reading CSV in chunks") as pbar:
            for chunk in pd.read_csv(DATA_FILE, chunksize=chunk_size):
                chunks.append(chunk)
                pbar.update(1)
        
        df = pd.concat(chunks, ignore_index=True)

    except FileNotFoundError:
        print(f"Error: Data file '{DATA_FILE}' not found.")
        print("Please run `create_training_data.py` first to generate the dataset.")
        return

    # Handle potential missing values
    df.dropna(subset=['description', 'priority'], inplace=True)
    
    X = df['description']
    y = df['priority']

    # 2. Split data into training and testing sets
    print("Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Create and train the TF-IDF Vectorizer
    print("Vectorizing text data using TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=1000) # Limit features to the top 1000 words
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # 4. Train the classification model
    print("Training the Logistic Regression model...")
    # Note: Scikit-learn's LogisticRegression doesn't have a built-in progress bar for training itself.
    # For more complex models (like in PyTorch/TensorFlow), you would wrap the training loop.
    model = LogisticRegression(random_state=42, class_weight='balanced')
    model.fit(X_train_tfidf, y_train)

    # 5. Evaluate the model
    print("\n--- Model Evaluation ---")
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    # Define labels to ensure correct order in the report
    labels = sorted(y.unique())
    print(classification_report(y_test, y_pred, labels=labels, zero_division=0))
    print("------------------------\n")

    # 6. Save the vectorizer and the model
    print(f"Saving vectorizer to '{VECTORIZER_FILE}'...")
    joblib.dump(vectorizer, VECTORIZER_FILE)
    
    print(f"Saving model to '{MODEL_FILE}'...")
    joblib.dump(model, MODEL_FILE)
    
    print("\nTraining complete. Model and vectorizer have been saved.")

if __name__ == "__main__":
    train_model()

