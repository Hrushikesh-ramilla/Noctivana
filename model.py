import torch
import torch.nn as nn

class CryClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
        )
        self.lstm = nn.LSTM(input_size=32 * 32, hidden_size=64, num_layers=1,
                            batch_first=True, bidirectional=True)
        self.attn = nn.Linear(128, 1)
        self.fc = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x: (B, 3, 128, T)
        x = self.cnn(x)                      # → (B, 32, H, W)
        B, C, H, W = x.shape
        x = x.permute(0, 3, 1, 2).reshape(B, W, C * H)  # (B, T, Features)
        lstm_out, _ = self.lstm(x)
        attn_weights = torch.softmax(self.attn(lstm_out), dim=1)  # (B, T, 1)
        context = torch.sum(attn_weights * lstm_out, dim=1)       # (B, 128)
        return self.fc(context).squeeze(1)  # (B,)
