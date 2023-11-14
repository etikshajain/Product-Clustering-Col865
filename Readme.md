### Problem Statement
Recommendation systems have become the backbone of the e-commerce platforms like Myntra, Amazon etc. In this work, we work with a dataset of products and users from an e-commerce site and try different clustering techniques to see which works the best. The work focuses on the use of Graph Neural Networks to create hidden representations for products and see how these embeddings can be used in addition/in replacement of the existing raw features.

### Modeling 
The problem is modeled as a graph which has two types of nodes, one representing users and others representing products. We create a bipartite graph such that an edge exists between a user node and a product node if the user has clicked on the product atleast once. Every node has its own features as well. The graph is created using the Deep Graph library (DGL) and visualised using networkx.

### Node Embeddings
After the graph is created, we train the graph using several techniques-
1. GAE
2. Link Prediction
3. GAE and link prediction using collaborative filtering features

### Clustering
Our aim is to obtain product clusters using embeddings and compare them with the clusters formed by raw features. We employed the following algorithms for product clustering-
1. K-means
2. DBScan

**References:**

1. https://dl.acm.org/doi/pdf/10.1145/3292500.3330925
2. https://dl.acm.org/doi/abs/10.14778/3402707.3402736
3. https://dl.acm.org/doi/abs/10.1145/3357384.3357924
