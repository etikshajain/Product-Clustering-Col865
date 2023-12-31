from __future__ import division
from __future__ import print_function

import time
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

# Train on CPU (hide GPU) due to memory constraints
os.environ['CUDA_VISIBLE_DEVICES'] = ""

import tensorflow.compat.v1 as tf
tf.compat.v1.disable_eager_execution()
import numpy as np
import scipy.sparse as sp

from sklearn.metrics import roc_auc_score
from sklearn.metrics import average_precision_score

from gae.input_dataa import load_data
from gae.optimizerr import OptimizerAE, OptimizerVAE
from gae.modell import GCNModelAE, GCNModelVAE
from gae.preprocessing import preprocess_graph, construct_feed_dict, sparse_to_tuple, mask_test_edges

# Settings
flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.01, 'Initial learning rate.')
flags.DEFINE_integer('epochs', 100, 'Number of epochs to train.')
flags.DEFINE_integer('hidden1', 32, 'Number of units in hidden layer 1.')
flags.DEFINE_integer('hidden2', 16, 'Number of units in hidden layer 2.')
flags.DEFINE_float('weight_decay', 0., 'Weight for L2 loss on embedding matrix.')
flags.DEFINE_float('dropout', 0., 'Dropout rate (1 - keep probability).')

flags.DEFINE_string('model', 'gcn_ae', 'Model string.')
flags.DEFINE_string('dataset', 'cora', 'Dataset string.')
flags.DEFINE_integer('features', 1, 'Whether to use features (1) or not (0).')

model_str = FLAGS.model
dataset_str = FLAGS.dataset

# Load data
adj, features, node_features = load_data(dataset_str)

# Store original adjacency matrix (without diagonal entries) for later
adj_orig = adj
adj_orig = adj_orig - sp.dia_matrix((adj_orig.diagonal()[np.newaxis, :], [0]), shape=adj_orig.shape)
adj_orig.eliminate_zeros()

adj_train, train_edges, val_edges, val_edges_false, test_edges, test_edges_false = mask_test_edges(adj)
adj = adj_train

if FLAGS.features == 0:
    features = sp.identity(features.shape[0])  # featureless

# Some preprocessing
adj_norm = preprocess_graph(adj)

# Define placeholders
placeholders = {
    'features': tf.sparse_placeholder(tf.float32),
    'adj': tf.sparse_placeholder(tf.float32),
    'adj_orig': tf.sparse_placeholder(tf.float32),
    'dropout': tf.placeholder_with_default(0., shape=())
}

num_nodes = adj.shape[0]

features = sparse_to_tuple(features.tocoo())
num_features = features[2][1]
features_nonzero = features[1].shape[0]

# Create model
model = None
if model_str == 'gcn_ae':
    model = GCNModelAE(placeholders, num_features, features_nonzero)
elif model_str == 'gcn_vae':
    model = GCNModelVAE(placeholders, num_features, num_nodes, features_nonzero)

pos_weight = float(adj.shape[0] * adj.shape[0] - adj.sum()) / adj.sum()
norm = adj.shape[0] * adj.shape[0] / float((adj.shape[0] * adj.shape[0] - adj.sum()) * 2)

# Optimizer
with tf.name_scope('optimizer'):
    if model_str == 'gcn_ae':
        opt = OptimizerAE(preds=model.reconstructions,
                          labels=tf.reshape(tf.sparse_tensor_to_dense(placeholders['adj_orig'],
                                                                      validate_indices=False), [-1]),
                          pos_weight=pos_weight,
                          norm=norm)
    elif model_str == 'gcn_vae':
        opt = OptimizerVAE(preds=model.reconstructions,
                           labels=tf.reshape(tf.sparse_tensor_to_dense(placeholders['adj_orig'],
                                                                       validate_indices=False), [-1]),
                           model=model, num_nodes=num_nodes,
                           pos_weight=pos_weight,
                           norm=norm)

# Initialize session
sess = tf.Session()
sess.run(tf.global_variables_initializer())

cost_val = []
acc_val = []


def get_roc_score(edges_pos, edges_neg, emb=None):
    if emb is None:
        feed_dict.update({placeholders['dropout']: 0})
        emb = sess.run(model.z_mean, feed_dict=feed_dict)

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    # Predict on test set of edges
    adj_rec = np.dot(emb, emb.T)
    preds = []
    pos = []
    for e in edges_pos:
        preds.append(sigmoid(adj_rec[e[0], e[1]]))
        pos.append(adj_orig[e[0], e[1]])

    preds_neg = []
    neg = []
    for e in edges_neg:
        preds_neg.append(sigmoid(adj_rec[e[0], e[1]]))
        neg.append(adj_orig[e[0], e[1]])

    preds_all = np.hstack([preds, preds_neg])
    labels_all = np.hstack([np.ones(len(preds)), np.zeros(len(preds_neg))])
    roc_score = roc_auc_score(labels_all, preds_all)
    ap_score = average_precision_score(labels_all, preds_all)

    return roc_score, ap_score, emb

def plot(arr, name):
    epochs_arr = np.arange(0, FLAGS.epochs)
    x = np.asarray(epochs_arr)
    ypoints = np.asarray(arr)
    plt.plot(x, ypoints)
    plt.xlabel("Epochs")
    plt.ylabel(name)
    plt.legend()
    plt.show()

def tsne(feats, featuress, name):
    tsne = TSNE(n_components=2, perplexity=30, n_iter=300)
    embeddings_2d = tsne.fit_transform(feats)

    color = featuress[:,1]

    plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], s=70, c=color)
    plt.title(name)
    plt.show()

def km(k,feats, name):
    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=k)
    clusters = kmeans.fit_predict(feats)

    # Scatter plot the results
    for cluster_id in range(k):
        plt.scatter(feats[clusters == cluster_id, 0], feats[clusters == cluster_id, 1], label=f'Cluster {cluster_id + 1}')

    # Plot the cluster centers
    cluster_centers = kmeans.cluster_centers_
    plt.scatter(cluster_centers[:, 0], cluster_centers[:, 1], marker='x', color='black', s=100, label='Cluster Centers')

    plt.title(f'K-Means Clustering (k={k}) of {name}')
    plt.legend()
    plt.show()

def dbs(eps, min_samples, featuress, feats):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(feats)

    # Create a scatter plot for the clusters
    plt.figure(figsize=(8, 6))
    plt.scatter(featuress[:,0], featuress[:,1], c=clusters, cmap='rainbow')
    plt.xlabel('Price')
    plt.ylabel('Vertical')
    plt.title(f'DBscan Clustering Results on raw features eps={eps} min_samples={min_samples}')
    plt.show()


cost_val = []
acc_val = []
val_roc_score = []

adj_label = adj_train + sp.eye(adj_train.shape[0])
adj_label = sparse_to_tuple(adj_label)

train_loss_arr=[]
val_roc_arr=[]
val_ap_arr=[]

# Train model
for epoch in range(FLAGS.epochs):

    t = time.time()
    # Construct feed dictionary
    feed_dict = construct_feed_dict(adj_norm, adj_label, features, placeholders)
    feed_dict.update({placeholders['dropout']: FLAGS.dropout})
    # Run single weight update
    outs = sess.run([opt.opt_op, opt.cost, opt.accuracy], feed_dict=feed_dict)

    # Compute average loss
    avg_cost = outs[1]
    avg_accuracy = outs[2]

    roc_curr, ap_curr, emb = get_roc_score(val_edges, val_edges_false)
    val_roc_score.append(roc_curr)

    train_loss_arr.append(avg_cost)
    val_roc_arr.append(roc_curr)
    val_ap_arr.append(ap_curr)


    print("Epoch:", '%04d' % (epoch + 1), "train_loss=", "{:.5f}".format(avg_cost),
          "train_acc=", "{:.5f}".format(avg_accuracy), "val_roc=", "{:.5f}".format(val_roc_score[-1]),
          "val_ap=", "{:.5f}".format(ap_curr),
          "time=", "{:.5f}".format(time.time() - t))

print("Optimization Finished!")
plot(train_loss_arr, 'Training loss')
plot(val_roc_arr, 'ROC')
plot(val_ap_arr, 'AP')

roc_score, ap_score, final_emb = get_roc_score(test_edges, test_edges_false)
print('Test ROC score: ' + str(roc_score))
print('Test AP score: ' + str(ap_score))
print(final_emb.shape)

# tsne(node_features, node_features, 't-SNE Visualization of raw features')
# tsne(final_emb, node_features,'t-SNE Visualization of embeddings')

# km(5,node_features, 'raw features')
# km(5,final_emb, 'embeddings')

# dbs(0.5, 5, final_emb, node_features)
# dbs(0.5, 50, final_emb, node_features)
# dbs(10, 5, final_emb, node_features)
# dbs(10, 50, final_emb, node_features)

dbs(0.5, 5, node_features, node_features)
dbs(0.5, 50, node_features, node_features)
dbs(10, 5, node_features, node_features)
dbs(10, 50, node_features, node_features)


