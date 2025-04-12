import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from dataset import CryDataset
from model import CryClassifier
from focal_loss import FocalLoss

# Hyperparameters
BATCH_SIZE = 32
EPOCHS = 25
LR = 1e-4

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Dataset and DataLoader
dataset = CryDataset("features/metadata.csv")
train_size = int(0.6 * len(dataset))
val_size = int(0.10 * len(dataset))
test_size = len(dataset) - train_size - val_size
train_ds, val_ds, test_ds = random_split(dataset, [train_size, val_size, test_size])
test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

# Model, Loss, Optimizer
model = CryClassifier().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
criterion = FocalLoss()

# Training loop
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for X, y in train_loader:
        X, y = X.to(device), y.to(device)
        preds = model(X)
        loss = criterion(preds, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # Evaluation
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for X, y in val_loader:
            X, y = X.to(device), y.to(device)
            p = model(X)
            predicted_labels = (p > 0.5).int().cpu().numpy().tolist()
            preds.extend(predicted_labels)
            targets.extend(y.int().cpu().numpy().tolist())

    acc = accuracy_score(targets, preds)
    f1 = f1_score(targets, preds)
    precision = precision_score(targets, preds)
    recall = recall_score(targets, preds)

    print(f"[{epoch+1}/{EPOCHS}] Loss: {total_loss:.4f} | Acc: {acc:.3f} | F1: {f1:.3f} | Precision: {precision:.3f} | Recall: {recall:.3f}")

# Save the model
torch.save(model.state_dict(), "cry_model1.pth")
print("✅ Model saved to cry_model1.pth")

# Final test evaluation
model.eval()
test_preds, test_targets = [], []

with torch.no_grad():
    for X, y in test_loader:
        X, y = X.to(device), y.to(device)
        p = model(X)
        predicted_labels = (p > 0.5).int().cpu().numpy().tolist()
        test_preds.extend(predicted_labels)
        test_targets.extend(y.int().cpu().numpy().tolist())

test_acc = accuracy_score(test_targets, test_preds)
test_f1 = f1_score(test_targets, test_preds)
test_precision = precision_score(test_targets, test_preds)
test_recall = recall_score(test_targets, test_preds)

print("\n🧪 Final Test Results:")
print(f"Accuracy:  {test_acc:.4f}")
print(f"F1 Score:  {test_f1:.4f}")
print(f"Precision: {test_precision:.4f}")
print(f"Recall:    {test_recall:.4f}")

# Plot confusion matrix
cm = confusion_matrix(test_targets, test_preds)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Not Crying", "Crying"], yticklabels=["Not Crying", "Crying"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()
