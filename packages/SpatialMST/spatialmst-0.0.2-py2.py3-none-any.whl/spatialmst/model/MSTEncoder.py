import torch
import torch.nn as nn
import torch.nn.functional as F
from spatialmst.modules.metabolic_modality import MetaboliteModality, ReactionModality
from spatialmst.modules.transcriptomic_modality import TranscriptomicModality
from spatialmst.layers.IntegrationLayer import IntegrationLayer


class MSTEncoder(nn.Module):
    """Spatial Multimodal Self-supervised Transformer"""
    def __init__(self, flux_in, flux_hidden, met_in, met_hidden, rna_in, rna_hidden, hidden_channels, out_channels, heads = 1):
        super(MSTEncoder, self).__init__()
        
        self.reaction_modality = ReactionModality(in_channels = flux_in, hidden_channels = flux_hidden, latent_channels = hidden_channels, heads=heads)
        self.metabolite_modality = MetaboliteModality(in_channels = met_in, hidden_channels = met_hidden, latent_channels = hidden_channels, heads=heads)
        self.transcriptomic_modality = TranscriptomicModality(in_channels = rna_in, hidden_channels = rna_hidden, out_channels = hidden_channels, heads=heads)
        
        self.metabolic_cross_attention = IntegrationLayer(hidden_channels, out_channels)
        self.metabolite_rxn_cross_attention = IntegrationLayer(hidden_channels, out_channels)      
        self.unified_embedding = nn.Linear(out_channels * 2, out_channels)
       
    def forward(self, flux_data, metabolite_data, transcriptomic_data, edge_index):
        reaction_out = self.reaction_modality(flux_data, edge_index)
        metabolite_out = self.metabolite_modality(metabolite_data, edge_index)
        transcriptomic_out = self.transcriptomic_modality(transcriptomic_data, edge_index)

        metabolic_embedding1 = self.metabolic_cross_attention(metabolite_out, reaction_out)
        metabolic_embedding2 = self.metabolic_cross_attention(reaction_out, metabolite_out)
        metabolic_embedding = metabolic_embedding1 + metabolic_embedding2
        unified_embedding1 = self.metabolite_rxn_cross_attention(transcriptomic_out, metabolic_embedding)
        unified_embedding2 = self.metabolite_rxn_cross_attention(metabolic_embedding, transcriptomic_out)
        unified_embedding = torch.cat((unified_embedding1, unified_embedding2), dim=-1)
        metabolic_embedding = F.normalize(metabolic_embedding, p=2, eps=1e-12, dim=1)  
        unified_embedding = F.normalize(unified_embedding, p=2, eps=1e-12, dim=1)
        unified_embedding = self.unified_embedding(unified_embedding)
        return metabolic_embedding, unified_embedding #x

