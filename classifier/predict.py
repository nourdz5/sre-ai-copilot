import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Load the saved model
tokenizer = DistilBertTokenizer.from_pretrained("./classifier/model")
model = DistilBertForSequenceClassification.from_pretrained("./classifier/model")
model.eval()

labels = {0: "P1", 1: "P2", 2: "P3"}

def classify_alert(alert_text):
    inputs = tokenizer(alert_text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted = torch.argmax(outputs.logits, dim=1).item()
    return labels[predicted]

if __name__ == "__main__":
    tests = [
        "Database is down, all connections refused",
        "HighMemoryUsage on payments-api, memory at 95%",
        "CPU at 60%, slightly elevated"
    ]
    for alert in tests:
        print(f"{classify_alert(alert)} — {alert}")
