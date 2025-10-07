import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class Norm(nn.Module):
    def __init__(self, d_model, dropout):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(d_model)
    
    def forward(self, attn):
        attn = self.dropout(attn)
        return self.norm(attn)


class TransformerLayer(nn.Module):
    def __init__(self, d_model, dropout=0.4):
        super().__init__()
        self.d_model = d_model
        self.Norm = Norm(d_model, dropout)
        
    def scaled_dot_product(self, q, k, v, mask=None):
        d_k = q.size()[-1]
        attn_logits = torch.matmul(q, k.transpose(-2, -1))
        attn_logits = attn_logits / math.sqrt(d_k)
        if mask is not None:
            attn_logits = attn_logits.masked_fill(mask == 0, -9e15)
        attention = F.softmax(attn_logits, dim=-1)
        values = torch.matmul(attention, v)
        return values, attention

    def forward(self, q, k, v, mask=None):
        x, _ = self.scaled_dot_product(q, k, v, mask=mask)
        x = self.Norm(x)
        return x


class IntegrationLayer(nn.Module):
    def __init__(self, dim, out_dim):
        super().__init__()
        self.qkv_proj = nn.Linear( 3 * dim, 3 * dim)
        self.attention_layer = TransformerLayer(dim)
        self.fc = nn.Linear(dim, out_dim)

    def forward(self, embd1, embd2, mask=None):
        q = embd1.unsqueeze(1)
        k = embd2.unsqueeze(1)
        v = embd2.unsqueeze(1)
        x = self.attention_layer(q, k, v, mask)       
        x = self.fc(x) 
        x = x.squeeze(1)
        return x

