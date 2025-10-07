import torch
from torch_geometric.nn import TransformerConv
import torch.nn.functional as F


class ReactionModality(torch.nn.Module):
    def __init__(self, in_channels = 168, hidden_channels = 32, latent_channels = 16, heads=1):
        super(ReactionModality, self).__init__()
        self.conv1 = TransformerConv(in_channels, hidden_channels, heads=heads)
        self.layernorm1 = torch.nn.LayerNorm(hidden_channels * heads)
        self.conv2 = TransformerConv(hidden_channels * heads, hidden_channels, heads=heads)
        self.layernorm2 = torch.nn.LayerNorm(hidden_channels * heads)
        self.conv3 = TransformerConv(hidden_channels * heads, latent_channels, heads=heads, concat = False)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.layernorm1(x)
        x = F.leaky_relu(x)
        x = self.conv2(x, edge_index)
        x = self.layernorm2(x)
        x = F.leaky_relu(x)
        x = self.conv3(x, edge_index)
        x = F.normalize(x)
        return F.leaky_relu(x)


class MetaboliteModality(torch.nn.Module):
    def __init__(self, in_channels = 70, hidden_channels = 32, latent_channels = 16, heads=1):
        super(MetaboliteModality, self).__init__()
        self.conv1 = TransformerConv(in_channels, hidden_channels, heads=heads)
        self.layernorm1 = torch.nn.LayerNorm(hidden_channels * heads)
        self.conv2 = TransformerConv(hidden_channels * heads, latent_channels, heads=heads, concat = False)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.layernorm1(x)
        x = F.leaky_relu(x)
        x = self.conv2(x, edge_index)
        x = F.normalize(x)
        return F.leaky_relu(x)
