import torch
import torch.nn.functional as F
import torch.optim as optim
import lightning as L
import numpy as np
import random
import os
from yaml import SafeLoader
import yaml

from spatialmst.model.MSTEncoder import MSTEncoder
from spatialmst.model.MSTDecoder import MSTDecoder
from spatialmst.utils.util import clustering

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class SpatialMSTModel(L.LightningModule):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.tau = self.config['tau']
        self.lr = self.config['lr']
        flux_in = self.config['flux_in']
        flux_hidden = self.config['flux_hidden']
        met_in = self.config['met_in']
        met_hidden = self.config['met_hidden']
        rna_in = self.config['rna_in']
        rna_hidden = self.config['rna_hidden']
        hidden_channels = self.config['hidden_channels']
        out_channels = self.config['out_channels']
        heads = self.config['heads']
        self.save_hyperparameters()

        self.model = MSTEncoder(flux_in, flux_hidden, met_in, met_hidden, rna_in, rna_hidden, hidden_channels, out_channels, heads = heads)
        self.decoder = MSTDecoder(input_latent_dim = out_channels, flux_out=flux_in, met_out=met_in, rna_out=rna_in, latent_dim = hidden_channels)
                    
    def forward(self, data):
        return self.predict(data)
    
    def configure_optimizers(self):
        self.optimizer = optim.Adam(self.parameters(), lr=self.lr, weight_decay= self.config['weight_decay'])
        return [self.optimizer]
        
    def sim(self, z1, z2):
        z1 = F.normalize(z1, p=2, dim=-1)
        z2 = F.normalize(z2, p=2, dim=-1)
        return torch.mm(z1, z2.t())

    def semi_loss(self, z1, z2):
        f = lambda x: torch.exp(x / self.tau)
        refl_sim = f(self.sim(z1, z1))
        between_sim = f(self.sim(z1, z2))

        return -torch.log(
            between_sim.diag()
            / (refl_sim.sum(1) + between_sim.sum(1) - refl_sim.diag()))
        
    
    def compute_contrastive_loss(self, h1, h2):        
        l1 = self.semi_loss(h1, h2)
        l2 = self.semi_loss(h2, h1)
        const_loss = 0.5 * (l1 + l2)
        const_loss = const_loss.mean()
        return const_loss
    
    def training_step(self, data):
        self.train()
        self.loss_gf = torch.nn.BCEWithLogitsLoss()
        flux_data, metabolite_data, rna_data, flux_data_a, metabolite_data_a, rna_data_a,  edge_index, graph_neigh, label_CSL, adj = data.flux, data.metabolite, data.rna,  data.flux_a, data.metabolite_a, data.rna_a, data.edge_index, data.graph_neigh, data.label_CSL, data.adj

        metabolic_embedding, unified_embedding = self.model(flux_data, metabolite_data, rna_data, edge_index)
        metabolic_embedding_a, unified_embedding_a = self.model(flux_data_a, metabolite_data_a, rna_data_a, edge_index)
        
        flux_recon, metabolite_recon, rna_recon = self.decoder(unified_embedding)
        
        met_cl_loss = self.compute_contrastive_loss(metabolic_embedding, metabolic_embedding_a)
        unified_cl_loss = self.compute_contrastive_loss(unified_embedding, unified_embedding_a)
        
        flux_rec_loss = F.mse_loss(flux_recon, flux_data)
        met_rec_loss = F.mse_loss(metabolite_recon, metabolite_data)
        rna_rec_loss = F.mse_loss(rna_recon, rna_data)
            
        loss = met_cl_loss + unified_cl_loss + flux_rec_loss + met_rec_loss + rna_rec_loss
        self.log("met_cl_loss", met_cl_loss)
        self.log("unified_cl_loss", unified_cl_loss)
        
        self.log("flux_rec_loss", flux_rec_loss)
        self.log("met_rec_loss", met_rec_loss)
        self.log("rna_rec_loss", rna_rec_loss)
        
        self.log("loss", loss)
        
        return loss

    def predict(self, data):
        self.eval()
        flux_data, metabolite_data, rna_data, edge_index = data.flux, data.metabolite, data.rna, data.edge_index
        metabolic_embedding, unified_embedding = self.model(flux_data, metabolite_data, rna_data, edge_index)        
        result = {}
        result['metabolic_embedding'] = metabolic_embedding
        result['unified_embedding'] = unified_embedding        
        
        return result

class SpatialMSTTrainer():
    def __init__(self, adata, config_file = None):
        super().__init__()
        seed = 42
        self.seed_everything(seed)
        torch.set_float32_matmul_precision('medium')
        self.adata = adata
        if config_file is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            config_file = os.path.join(base_dir, 'config.yaml')
        self.config = yaml.load(open(config_file), Loader=SafeLoader)['Hyperparameters']
        
        for mod in self.adata.mod:
            self.config[mod + '_in'] = self.adata.mod[mod].X.shape[1]
        self.model = SpatialMSTModel(self.config)
    
    def seed_everything(self, seed: int):
        L.seed_everything(seed, workers=True)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def train_model(self, data, epochs=None):
        if epochs is None:
            epochs = self.config['epochs']
            
        self.trainer = L.Trainer(
            # default_root_dir=CHECKPOINT_PATH,
            logger=False,
            accelerator="auto",
            deterministic=True,
            devices=1,
            max_epochs=epochs,
            log_every_n_steps=1,
            enable_checkpointing=False
        )

        self.trainer.fit(self.model, data)

        return self.model

    def predict(self, trained_model, data, num_cluster= 7, method = "mclust"):
        predictions = self.trainer.predict(trained_model, data)
        self.adata.obsm['metabolic_embedding'] = predictions[0]['metabolic_embedding'].detach().cpu().numpy()
        self.adata.obsm['unified_embedding'] = predictions[0]['unified_embedding'].detach().cpu().numpy()
        clustering(self.adata,method=method, use_rep='unified_embedding', n_clusters= num_cluster)
        return self.adata