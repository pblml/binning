import math
import numpy as np
from itertools import zip_longest, chain
import json
from tqdm import tqdm
from collections import defaultdict
from sklearn.cluster import KMeans
from visualizing import draw_graph, draw_overlap, draw_diffs
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import random

np.random.seed(42)

def simulate_paths(S0 = 100., K = 200., T = 1.0, r = 0.05, sigma = 0.2, M = 5, I = 100):
    dt = T/M
    #I Paths with M timesteps

    S = np.zeros(shape = (M+1, I))
    S[0] = S0

    for t in range(1, M+1):
        z = np.random.standard_normal(I)
        S[t] = S[t-1] * np.exp((r-0.5*sigma**2)*dt + sigma*math.sqrt(dt)*z)

    return(S)


    res = defaultdict(list)
    try:
        kmeans = KMeans(n_clusters=n, init='k-means++', random_state=0).fit(S_t.reshape(-1,1))
        tpl_list = [(j, i) for i, j in zip(S_t, kmeans.labels_)]
        for i, j in tpl_list:
            res[f"bin{i}"].append(j)
        res_list = sorted(list(res.values()), key=lambda x: min(x))
        for i in range(n):
            res[f"bin{i}"]=res_list[i]
    except Exception as e:
        for i in range(n):
            res[f"bin{i}"]=[100]
    return res

def binning_S(S, nbins=4, method="kmeans"):
    n = int(len(S[0])/nbins)
    res_dict = dict()
    #for every timestep
    for i in tqdm(range(S.shape[0]), desc=f"binning using {method}"):
        if method=="kmeans":
            res_dict[f"t{i}"] = binning_t_kmeans(S[i], n=nbins)
        elif method=="fixed":
            res_dict[f"t{i}"] = binning_t_fs(S[i], n=n)
    return res_dict

def pivot_bins(t_dict):
    b_dict = dict()
    for b in t_dict["t1"].keys():
        for t in t_dict.keys():
            b_dict[b] = {i[0]: i[1][b] for i in t_dict.items()}
    return b_dict

def get_diffs(bins1, bins2, bin=[0]):
    res_dict = {}
    for x in bins1.keys(): #bins
        if x in ["".join(["bin", str(i)]) for i in bin]:
            res_dict[x]=[]
            for idx, (i, j) in enumerate(zip(bins1[x].values(), bins2[x].values())): #idx=t
                res_dict[x].append(abs(max(i)-max(j))+abs(min(i)-min(j)))

    return res_dict
