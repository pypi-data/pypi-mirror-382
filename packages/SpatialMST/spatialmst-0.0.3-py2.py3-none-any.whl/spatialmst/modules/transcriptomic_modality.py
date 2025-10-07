import torch.nn as nn
from torch_geometric.nn import TransformerConv
import torch.nn.functional as F

class TranscriptomicModality(nn.Module):
    def __init__(self, in_channels = -1, hidden_channels = 64, out_channels = 32, heads=1):
        super(TranscriptomicModality, self).__init__()
        self.conv1 = TransformerConv(in_channels, hidden_channels, heads=heads)
        self.layernorm1 = nn.LayerNorm(hidden_channels * heads)
        self.conv2 = TransformerConv(hidden_channels * heads, hidden_channels, heads=heads)
        self.layernorm2 = nn.LayerNorm(hidden_channels * heads)
        self.conv3 = TransformerConv(hidden_channels * heads, hidden_channels, heads=heads)
        self.layernorm3 = nn.LayerNorm(hidden_channels * heads)
        self.conv4 = TransformerConv(hidden_channels * heads, out_channels, heads=heads, concat = False)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.layernorm1(x)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        x = self.layernorm2(x)
        x = F.relu(x)
        x = self.conv3(x, edge_index)
        x = self.layernorm3(x)
        x = F.relu(x)
        x = self.conv4(x, edge_index)
        x = F.relu(x)
        x = F.normalize(x)
        return x
