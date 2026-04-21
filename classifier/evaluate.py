import torch
import csv
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

# Load data
texts, labels = [], []
with open("data/alerts.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) == 2:
            texts.append(row[0])
            labels.append(row[1])

# Encode labels
le = LabelEncoder()
encoded_labels = le.fit_transform(labels)

# Same split as training — same random_state = same test set
_, test_texts, _, test_labels = train_test_split(
    texts, encoded_labels, test_size=0.2, random_state=42
)

# Load saved model
tokenizer = DistilBertTokenizer.from_pretrained("./classifier/model")
model = DistilBertForSequenceClassification.from_pretrained("./classifier/model")
model.eval()

# Run predictions
predictions = []
for text in test_texts:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted = torch.argmax(outputs.logits, dim=1).item()
    predictions.append(predicted)

# Print metrics
print(classification_report(test_labels, predictions, target_names=le.classes_))
accuracy = accuracy_score(test_labels, predictions)
print(f"Overall accuracy: {accuracy:.2%}")
