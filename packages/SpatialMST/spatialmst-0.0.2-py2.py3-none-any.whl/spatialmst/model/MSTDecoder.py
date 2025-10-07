import torch.nn as nn

class MSTDecoder(nn.Module):
    """Decoder for reconstructing multi-modal data from unified_embedding"""
    def __init__(self, input_latent_dim, flux_out, met_out, rna_out, latent_dim=64):
        super(MSTDecoder, self).__init__()

        self.flux_decoder = nn.Sequential(
            nn.Linear(input_latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, flux_out)
        )

        self.metabolite_decoder = nn.Sequential(
            nn.Linear(input_latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, met_out)
        )

        self.rna_decoder = nn.Sequential(
            nn.Linear(input_latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, rna_out //2),
            nn.ReLU(),
            nn.Linear(rna_out // 2, rna_out),
            nn.ReLU()
        )

    def forward(self, unified_embedding):
        flux_recon = self.flux_decoder(unified_embedding)
        metabolite_recon = self.metabolite_decoder(unified_embedding)
        rna_recon = self.rna_decoder(unified_embedding)
        
        return flux_recon, metabolite_recon, rna_recon

