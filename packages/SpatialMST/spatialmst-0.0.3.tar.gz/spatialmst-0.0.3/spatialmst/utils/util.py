import ot
import torch
import scanpy as sc
import scipy.sparse as sp
import scanpy.external as sce
from mudata import MuData
import pandas as pd
import numpy as np
import sklearn.neighbors

from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import fowlkes_mallows_score
from sklearn.metrics.cluster import homogeneity_score
from sklearn.metrics.cluster import adjusted_mutual_info_score
from sklearn.metrics.cluster import completeness_score



def search_res(adata, n_clusters, method='leiden', use_rep='embedding', start=0.01, end=3.0, increment=0.01):
    label = 0
    sc.pp.neighbors(adata, n_neighbors=50, use_rep=use_rep)
    for res in sorted(list(np.arange(start, end, increment)), reverse=False):
        if method == 'leiden':
           sc.tl.leiden(adata, random_state=0, resolution=res)
           count_unique = len(pd.DataFrame(adata.obs['leiden']).leiden.unique())
        elif method == 'louvain':
           sc.tl.louvain(adata, random_state=0, resolution=res)
           count_unique = len(pd.DataFrame(adata.obs['louvain']).louvain.unique()) 
        if count_unique == n_clusters:
            label = 1
            break

    assert label==1, "Resolution is not found. Please try bigger range or smaller step!." 
    print('Resolution: %.10f, Number of clusters: %d' % (res, count_unique))
    return res  

def refine_label(adata, radius=50, key='label'):
    new_type = []
    old_type = adata.obs[key].values

    coor = pd.DataFrame(adata.obsm['spatial'])
    coor.index = adata.obs.index

    nbrs = sklearn.neighbors.NearestNeighbors(radius=radius).fit(coor)
    distances, indices = nbrs.radius_neighbors(coor, return_distance=True)

    n_cell = indices.shape[0]
    for it in range(n_cell):
        neigh_type = [old_type[i] for i in indices[it]]
        max_type = max(neigh_type, key=neigh_type.count)
        new_type.append(int(max_type))
    new_type = np.array([str(i) for i in list(new_type)])
    return new_type


def mclust_R(adata, num_cluster, modelNames='EEE', used_obsm='emb_pca', random_seed=42):
    
    np.random.seed(random_seed)
    import rpy2.robjects as robjects
    robjects.r.library("mclust")

    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    r_random_seed = robjects.r['set.seed']
    r_random_seed(random_seed)
    rmclust = robjects.r['Mclust']
    
    res = rmclust(rpy2.robjects.numpy2ri.numpy2rpy(adata.obsm[used_obsm]), num_cluster, modelNames)
    mclust_res = np.array(res[-2])

    adata.obs['domain'] = mclust_res
    adata.obs['domain'] = adata.obs['domain'].astype('int')
    adata.obs['domain'] = adata.obs['domain'].astype('category')
    return adata



def clustering(adata, n_clusters=7, radius=50, method='mclust', use_rep='unified_embedding', start=0.01, end=3.0, increment=0.001, refinement=True):
    print("identifying domains...")
    # from sklearn.decomposition import PCA
    # pca = PCA(n_components=20, random_state=42) 
    # embedding = pca.fit_transform(adata.obsm[use_rep].copy())
    # adata.obsm['emb_pca'] = embedding
    # use_rep = 'emb_pca'
    
    if method == 'mclust':
        adata = mclust_R(adata, used_obsm=use_rep, num_cluster=n_clusters)
          
    if method == 'leiden':
       res = search_res(adata, n_clusters, method=method, use_rep=use_rep, start=start, end=end, increment=increment)
       sc.tl.leiden(adata,key_added="domain", random_state=0, resolution=res)
    #    adata.obs['domain'] = adata.obs['leiden']
    elif method == 'louvain':
       res = search_res(adata, n_clusters, method=method, use_rep=use_rep, start=start, end=end, increment=increment)
       sc.tl.louvain(adata, key_added="domain", random_state=0, resolution=res)
    #    adata.obs['domain'] = adata.obs['louvain'] 
       
    if refinement:  
       new_type = refine_label(adata, radius, key='domain')
       adata.obs['domain'] = new_type 
       adata.obs['domain'] = adata.obs['domain'].astype('category')
       
       
def cluster_metrics(target, pred):
    target = np.array(target)
    pred = np.array(pred)
    
    ari = adjusted_rand_score(target, pred)
    ami = adjusted_mutual_info_score(target, pred)
    nmi = normalized_mutual_info_score(target, pred)
    fmi = fowlkes_mallows_score(target, pred)
    comp = completeness_score(target, pred)
    homo = homogeneity_score(target, pred)
    print('ARI: %.3f, AMI: %.3f, NMI: %.3f, FMI: %.3f, Comp: %.3f, Homo: %.3f' % (ari, ami, nmi, fmi, comp, homo))
    
    return ari, ami, nmi, fmi, comp, homo
      


def construct_mm_adata(rna_path, flux_path, metabolite_path, metabolic_metadata_path):
    """
    Construct adata object for multi-omics analysis.
    Parameters
    ----------
    rna_path: .h5ad file path, 
    flux_path: .csv file path, 
    metabolite_path: .csv file path, 
    metabolic_metadata_path: .csv file path
    Returns
        MuData
    """
    rna_adata = sc.read_h5ad(rna_path)
    rna_adata.var_names_make_unique(join="/")
    sc.pp.normalize_total(rna_adata,target_sum=10e4)
    sc.pp.log1p(rna_adata)
    sc.pp.scale(rna_adata, zero_center=False, max_value=10)

    sce.pp.magic(rna_adata, name_list='all_genes', knn=3)
    flux_metadata = pd.read_csv(metabolic_metadata_path, index_col=0)
    flux = pd.read_csv(flux_path, index_col=0)
    flux.columns = flux_metadata['rxnName']
    metabolite = pd.read_csv(metabolite_path, index_col=0)
    flux = flux[flux.index.isin(rna_adata.obs.index)]
    metabolite = metabolite[metabolite.index.isin(rna_adata.obs.index)]

    mdata = MuData({'rna': rna_adata, 
                    'flux': sc.AnnData(flux), 
                    'metabolite': sc.AnnData(metabolite)}
                   )
    mdata['flux'].var = flux_metadata
    mdata['flux'].var.index = flux_metadata['rxnName']

    mdata.uns  = rna_adata.uns 
    # mdata.obsm['X_pca'] =  rna_adata.obsm['X_pca']
    mdata.obsm['spatial'] = rna_adata.obsm['spatial']
    mdata.uns['spatial'] = rna_adata.uns['spatial']
    mdata['flux'].obsm['spatial'] = rna_adata.obsm['spatial']
    mdata['flux'].uns['spatial'] = rna_adata.uns['spatial']
    mdata['metabolite'].obsm['spatial'] = rna_adata.obsm['spatial']
    mdata['metabolite'].uns['spatial'] = rna_adata.uns['spatial']
    
    add_contrastive_label(mdata)
    mdata.pull_obs()

    return mdata

########

def permute_features(feature):
    
    ids = np.arange(feature.shape[0])
    ids = np.random.permutation(ids)
    feature_permutated = feature[ids]

    return feature_permutated

def add_contrastive_label(adata):
    # contrastive label
    n_spot = adata.n_obs
    one_matrix = np.ones([n_spot, 1])
    zero_matrix = np.zeros([n_spot, 1])
    label_CSL = np.concatenate([one_matrix, zero_matrix], axis=1)
    adata.obsm['label_CSL'] = label_CSL
    