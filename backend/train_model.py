import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib

# Load the data
print("Loading training data...")
df = pd.read_csv('training_data.csv')

# Separate features and labels
X = df.drop('label', axis=1)
y = df['label']

print(f"Features shape: {X.shape}")
print(f"Labels shape: {y.shape}")

# Split data into training (80%) and testing (20%)
print("\nSplitting data into training and testing sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set: {X_test.shape[0]} samples")

# Train Random Forest model
print("\n🧠 Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("✅ Model trained!")

# Make predictions
print("\n📊 Evaluating model...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"\n📈 MODEL PERFORMANCE METRICS:")
print(f"Accuracy:  {accuracy:.2%}")
print(f"Precision: {precision:.2%}")
print(f"Recall:    {recall:.2%}")
print(f"F1-Score:  {f1:.2%}")

print(f"\n🔍 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Human', 'Bot', 'Suspicious']))

print(f"\n📋 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save the model
print("\n💾 Saving model...")
joblib.dump(model, 'bot_detector.joblib')
print("✅ Model saved as bot_detector.joblib")

# Test the model with a sample prediction
print("\n🧪 Test prediction with sample data:")
sample = X_test.iloc[0:1]
prediction = model.predict(sample)
probability = model.predict_proba(sample)

label_names = {0: 'Human', 1: 'Bot', 2: 'Suspicious'}
pred_label = label_names[prediction[0]]
confidence = probability[0][prediction[0]]

print(f"Prediction: {pred_label}")
print(f"Confidence: {confidence:.2%}")
print(f"All probabilities: Human={probability[0][0]:.2%}, Bot={probability[0][1]:.2%}, Suspicious={probability[0][2]:.2%}")

print("\n✅ Training complete! Model is ready for deployment.")