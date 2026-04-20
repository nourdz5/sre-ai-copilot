import mlflow
import torch
import csv
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset

# Load data
texts, labels = [], []
with open("data/alerts.csv") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if len(row) == 2:
            texts.append(row[0])
            labels.append(row[1])

# Encode labels: P1=0, P2=1, P3=2
le = LabelEncoder()
encoded_labels = le.fit_transform(labels)

# Split into train and test
train_texts, test_texts, train_labels, test_labels = train_test_split(
    texts, encoded_labels, test_size=0.2, random_state=42
)

# Tokenize
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

class AlertDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

train_dataset = AlertDataset(train_texts, train_labels.tolist())
test_dataset = AlertDataset(test_texts, test_labels.tolist())

# Load model
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=3
)

# Train
mlflow.set_experiment("alert-classifier")
with mlflow.start_run():
    training_args = TrainingArguments(
        output_dir="./classifier/output",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_dir="./classifier/logs",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
    )

    trainer.train()

    # Log metrics to MLflow
    metrics = trainer.evaluate()
    mlflow.log_metrics(metrics)
    mlflow.log_param("epochs", 3)
    mlflow.log_param("model", "distilbert-base-uncased")

    # Save model
    model.save_pretrained("./classifier/model")
    tokenizer.save_pretrained("./classifier/model")
    print("Model saved to classifier/model")
    print(f"Eval loss: {metrics['eval_loss']:.4f}")
