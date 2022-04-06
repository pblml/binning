import math
import numpy as np
from itertools import zip_longest, chain
import json
from tqdm import tqdm
from collections import defaultdict
from sklearn.cluster import KMeans
from visualizing import draw_graph2, get_diffs, draw_diffs

np.random.seed(42)

def simulate_paths(S0 = 100., K = 200., T = 1.0, r = 0.05, sigma = 0.2, M = 100, I = 1000):
    dt = T/M
    #I Paths with M timesteps

    S = np.zeros(shape = (M+1, I))
    S[0] = S0

    for t in range(1, M+1):
        z = np.random.standard_normal(I)
        S[t] = S[t-1] * np.exp((r-0.5*sigma**2)*dt + sigma*math.sqrt(dt)*z)

    return(S)


def binning_t_fs(S_t, n=4):
    sorted = np.sort(S_t)
    return {f"bin{idx}": list(item) for idx, item in enumerate(list(zip_longest(*[iter(sorted)]*n, fillvalue="")))}

def binning_t_kmeans(S_t, n=4):
    #bin{idx}: [1,2,3,...]
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
        print(e)
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


S = simulate_paths(sigma=0.2)
fs_bins = pivot_bins(binning_S(S=S, method='fixed'))
kmeans_bins = pivot_bins(binning_S(S=S, method='kmeans'))
# with open("diffs.json", "w") as f:
#     f.write(json.dumps(get_diffs(fs_bins, kmeans_bins, S[:, -4:], bin=[0,1,2,3])))
#draw_graph2(fs_bins, kmeans_bins, S[:, -4:], bin=[0,3])
draw_diffs(get_diffs(fs_bins, kmeans_bins, S[:, -4:], bin=[0,1,2,3]))

#{t1: {b1: [s1, s2, s3], b2: [s4, s5, s6]},
# t2: {b1: [s1, s2, s3]}}
