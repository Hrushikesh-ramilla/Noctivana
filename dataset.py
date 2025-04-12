import torch
import numpy as np
import pandas as pd
from torch.utils.data import Dataset

class CryDataset(Dataset):
    def __init__(self, csv_path):
        df = pd.read_csv(csv_path)
        self.paths = df['path'].tolist()
        self.labels = df['label'].tolist()

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        features = np.load(self.paths[idx])
        features = torch.tensor(features, dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.float32)
        return features, label
