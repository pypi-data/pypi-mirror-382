import scanpy as sc
import torch
from torch_geometric.data import Data
from sklearn.neighbors import kneighbors_graph
from scipy.sparse.csc import csc_matrix
from scipy.sparse.csr import csr_matrix
import scipy.sparse as sp
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MaxAbsScaler

class SpatialDataset(Dataset):
    def __init__(self, adata, k = None):
        self.adata = adata
        if k is None:
            k = self._optimize_k(adata)
        self.K = k
        self.data = self.construct_graph_data(self.adata, self.K)
    
    def _optimize_k(self, adata):
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        k_range=[10,13,15,20,25,30,35,40,45,50]
        x = np.concatenate((adata['rna'].X, adata['flux'].X, adata['metabolite'].X), axis=1)
        x = scaler.fit_transform(x)
        moran_scores = []
        for k in k_range:
            g = kneighbors_graph(adata.obsm['spatial'], k, mode='distance', include_self=False)
            moranI = sc.metrics.morans_i(g, x.T)
            moran_scores.append(np.nanmax(moranI))
        moran_scores = np.array(moran_scores)
        # select the k with maximum score    
        best_k = k_range[np.argmax(moran_scores)]
        print(f"identified best k: {best_k}")
        return best_k
            
    
    def knn_permutation(self, feature, edge_index, k=5):

        N = feature.shape[0]
        perm_feature = feature.clone()

        for node in range(N):
            neighbors = edge_index[1][edge_index[0] == node]
            if len(neighbors) > k:
                neighbors = np.random.choice(neighbors.cpu().numpy(), k, replace=False)
            elif len(neighbors) == 0:
                continue  # Skip isolated nodes

            swap_idx = np.random.choice(neighbors)
            perm_feature[node] = feature[swap_idx]

        return perm_feature

    def construct_graph_data(self, adata, K = 10):
        scalar = MaxAbsScaler()        
        spatial_coords = adata.obsm['spatial']
        adjacency_matrix = kneighbors_graph(spatial_coords, n_neighbors=K, mode='connectivity', include_self=False)
        edge_index = torch.tensor(adjacency_matrix.nonzero(), dtype=torch.long)
        
        graph_neigh = adjacency_matrix.toarray()
        adata.obsm['graph_neigh'] = graph_neigh

        adj = graph_neigh + graph_neigh.T
        adj = np.where(adj > 1, 1, adj)
        adata.obsm['adj'] = adj
                
        if isinstance(adata.mod['rna'].X, csc_matrix) or isinstance(adata.mod['rna'].X, csr_matrix):
            feat = adata.mod['rna'].X.toarray()[:, ]
        else:
            feat = adata.mod['rna'].X[:, ] 
        rna_features = torch.tensor(feat, dtype=torch.float)
        metabolite_features = scalar.fit_transform(np.array(adata.mod['metabolite'].X))
        metabolite_features = torch.tensor(metabolite_features, dtype=torch.float)
        flux_features = scalar.fit_transform(np.array(adata.mod['flux'].X))
        flux_features = torch.tensor(flux_features, dtype=torch.float)
        adj= torch.tensor(adata.obsm['adj'], dtype=torch.long)
        graph_neigh = torch.FloatTensor(adata.obsm['graph_neigh'].copy() + np.eye(adj.shape[0]))
        label_CSL = torch.FloatTensor(adata.obsm['label_CSL'])
        
        flux_features_a = self.knn_permutation(flux_features, edge_index, k=self.K)
        metabolite_features_a = self.knn_permutation(metabolite_features, edge_index, k=self.K)
        rna_features_a = self.knn_permutation(rna_features, edge_index, k=self.K)
        
        
        data = Data(rna=rna_features, flux = flux_features, metabolite = metabolite_features, 
                    rna_a=rna_features_a, flux_a = flux_features_a, metabolite_a = metabolite_features_a,
                    edge_index=edge_index, num_nodes = rna_features.shape[0], graph_neigh= graph_neigh, adj= adj, label_CSL= label_CSL)
        
        return data

    def __len__(self):
        return 1  # Single graph dataset 

    def __getitem__(self, idx):
        return self.data



