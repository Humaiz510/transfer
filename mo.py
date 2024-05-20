import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the CSV file
df = pd.read_csv('inspector_findings.csv')

# Preprocess the data (example: binary classification for simplicity)
df['label'] = df['severity'].apply(lambda x: 1 if x == 'High' else 0)

# Feature engineering (using TF-IDF for the description)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['description'])
y = df['label']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Predict on the entire dataset and add the column
df['model_assessment'] = model.predict(vectorizer.transform(df['description']))

# Save the updated CSV file
df.to_csv('inspector_findings_with_assessment.csv', index=False)