import torch
import csv
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import shutil
import os

def evaluate_model(model_path, test_texts, test_labels):
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    model.eval()

    predictions = []
    for text in test_texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)
        predicted = torch.argmax(outputs.logits, dim=1).item()
        predictions.append(predicted)

    return accuracy_score(test_labels, predictions)

# Load data
texts, labels = [], []
with open("data/alerts.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) == 2:
            texts.append(row[0])
            labels.append(row[1])

le = LabelEncoder()
encoded_labels = le.fit_transform(labels)

_, test_texts, _, test_labels = train_test_split(
    texts, encoded_labels, test_size=0.2, random_state=42
)

# Find latest checkpoint dynamically instead of hardcoding
import glob
checkpoints = sorted(glob.glob("./classifier/output/checkpoint-*"), key=os.path.getmtime)
if not checkpoints:
    print("No checkpoint found in classifier/output — run train.py first")
    exit(1)
new_model_path = checkpoints[-1]
current_model_path = "./classifier/model"
print(f"Comparing new checkpoint: {new_model_path}")

print("Evaluating current model...")
current_accuracy = evaluate_model(current_model_path, test_texts, test_labels)
print(f"Current model accuracy: {current_accuracy:.2%}")

print("Evaluating new model...")
new_accuracy = evaluate_model(new_model_path, test_texts, test_labels)
print(f"New model accuracy: {new_accuracy:.2%}")

if new_accuracy > current_accuracy:
    print(f"New model is better ({new_accuracy:.2%} vs {current_accuracy:.2%}) — promoting")
    shutil.copytree(new_model_path, current_model_path, dirs_exist_ok=True)
    print("Model promoted successfully")
else:
    print(f"Current model is better ({current_accuracy:.2%} vs {new_accuracy:.2%}) — keeping current")
