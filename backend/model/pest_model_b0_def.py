import torch.nn as nn
from torchvision import models

class PestClassifier(nn.Module):
    def __init__(self, num_classes):
        super(PestClassifier, self).__init__()
        # Load pre-trained EfficientNet-B0
        self.model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)

        # Replace the final classification layer
        in_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.model(x)
