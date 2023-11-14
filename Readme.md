### Why learn graph representations without labels?
1. TL
2. Get node embeddings for graph clustering

### Till now- 
1. There exist clustering algos but they do not take node features into account
2. Self supervised learning- Remove edges and nodes and make the model predict those parts

### Col865
- This project aims to analyze the quality of product node embeddings obtained by various GNN architectures, including classic models such as GCNs, GraphSAGE and recent models such as ClusterGCN[1], HINs [2], and other augmented approaches[3].
- The analysis can be targeted based on the following questions:
    - Can techniques like ClusterGCN be applied to heterogenous networks that are handled by HINs?
    - How do the clusters formed by node embeddings by different models compare against clusters formed by actual node features?

**References:**

1. https://dl.acm.org/doi/pdf/10.1145/3292500.3330925
2. https://dl.acm.org/doi/abs/10.14778/3402707.3402736
3. https://dl.acm.org/doi/abs/10.1145/3357384.3357924

### Three ways to perform representational learning without labels:
1. Autoencoders- Reconstruct the adj matrix or node features
2. Task generation- descriptors- node degrees, path lengths - task will be to predict these descriptors
3. Contrasive

## Autoencoders
1. Variational graph Autoencoders- Reconstructs adj matrix, the node embeddings are optimized such that the recontructed adj matrix preserves connectivity. paper[`https://arxiv.org/pdf/1611.07308.pdf`] code[`https://github.com/tkipf/gae`]
2. Strategies for pre training GNNs- Attribute masking- mask certain features and then reconstructs node features, embeddings are optimized to preserve the context of nodes 


## Aim:
1. Data analysis
2. Obtain embeddings of your hetero dataset properly using one of the implementations from 
    1. paper[`https://arxiv.org/pdf/1611.07308.pdf`] --> Apply GAE on data as link pred task --> modify for bip graph --> remove edges from dataset that will be predicted by model and accuracy will be calculated accordingly.
    2. Graph-sc
    3. Strategies for pre training GNNs
    4. link-pred task in bipartite graph
3. Visualise and compare embeddings
4. Training analysis
5. Build recomm system using this
6. clustering
7. Try a new tukka method to obtain embeddings

## Tricks
[2:20 pm, 11/10/2023] Vanshita IITD: metrics- loss, acc, roc, auc, ap
[2:20 pm, 11/10/2023] Vanshita IITD: visualization embeddings and feature vector compare
[2:23 pm, 11/10/2023] Vanshita IITD: padding
[2:24 pm, 11/10/2023] Vanshita IITD: adj matrix
[2:25 pm, 11/10/2023] Vanshita IITD: hetero approach


data size
loss fn
normalisation
encoding
lr
reg
adj matrix weight
feature dimension
model complexity - layers


-collab filtering results - take from anjali
-AE as homo - done
-use collab filtering for feature extraction for AE as homo - done
-link pred - pyg as hetero - done
-clustering with all above and compare with direct clustering
-node class - popularity of products
-HIN
-hin with AE
-