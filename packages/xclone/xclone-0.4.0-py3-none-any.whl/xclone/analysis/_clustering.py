"""Base functions for XClone clustering analysis.
"""
import numpy as np
def XClustering(Xdata, 
                Xlayer, 
                n_clusters = 5, 
                method = "k-means", 
                reshape = True, 
                argmaxprob = False,
                PCA = True, 
                PCA_comp = 30):
    """

    """
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.cluster import AgglomerativeClustering
    import umap

    if reshape:
        cell_num = Xdata.shape[0]
        X_use = Xdata.layers[Xlayer].reshape(cell_num, -1)
    elif argmaxprob:
        X_use = np.argmax(Xdata.layers[Xlayer], axis=2)
    else:
        X_use = Xdata.layers[Xlayer]
        
    
    ## PCA
    if PCA:
        data = PCA(n_components=PCA_comp).fit_transform(X_use)
    else:
        data = X_use.copy()

    
    ## Clustering
    if method == "k-means":
        kmeans = KMeans(init="k-means++", n_clusters=n_clusters, n_init=4)
        kmeans.fit(data)
        Z = kmeans.predict(data)
        
    if method == "Hierarchical":
        clustering = AgglomerativeClustering(n_clusters = n_clusters).fit(data)
        Z = clustering.labels_
    
    ## UMAP
    reducer = umap.UMAP()
    embedding = reducer.fit_transform(data)
    
    
    return Z, embedding



def XClustering2(Xdata, Xlayer, PCA_comp = 30, n_clusters = 5, method = "k-means"):
    from sklearn.cluster import KMeans
    from sklearn.cluster import AgglomerativeClustering
    import umap
    import numpy as np

    X_use = np.argmax(Xdata.layers[Xlayer], axis=2)
    reduced_data = X_use.copy()
    
    ## Clustering
    if method == "k-means":
        kmeans = KMeans(init="k-means++", n_clusters=n_clusters, n_init=4)
        kmeans.fit(reduced_data)
        Z = kmeans.predict(reduced_data)
        
    if method == "Hierarchical":
        clustering = AgglomerativeClustering(n_clusters = n_clusters).fit(reduced_data)
        Z = clustering.labels_
    
    ## UMAP
    reducer = umap.UMAP()
    embedding = reducer.fit_transform(reduced_data)
    
    
    return Z, embedding






def Cluster_mapping(Xdata,
                    pre_anno,
                    after_anno,
                    mapping_mode = 1,
                    defined_anno_dic = None):
    """
    Function:
    ---------
    define dic for clone int and str mapping.
    e.g., cluster2annotation = {
     0: 'Cluster1',
     1: 'Cluster2',
     2: 'Cluster3'}

    Example:
    --------
    Xdata = Cluster_mapping(Xdata, pre_anno = "cnv_clone2", after_anno = "xclone2")
    """
    # define a dictionary to map clone to annotation label
    clone2annotation = {}
    for i in range(0,100):
        clone2annotation[i] = "Clone"+str(i+1)
    # define a dictionary to map cluster to annotation label
    cluster2annotation = {}
    for i in range(0,100):
        cluster2annotation[i] = "Cluster"+str(i+1)
    
    ## select mapping annotation
    if mapping_mode == 1:
        map_annotation = clone2annotation
    if mapping_mode == 2:
        map_annotation = cluster2annotation
    if mapping_mode == 3:
        map_annotation = defined_anno_dic
    
    ## mapping
    Xdata.obs[after_anno] = Xdata.obs[pre_anno].map(map_annotation).astype('category')
    return Xdata