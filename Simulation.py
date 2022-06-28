import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from itertools import zip_longest
from tqdm import tqdm
import math
from sklearn.cluster import KMeans

np.random.seed(0)

class Simulation():

    def __init__(self):
        self.data = None
        self.bin_data = None
        self.edgelist = None

    def generate(self, S0 = 100., T = 1.0, r = 0.05, sigma = 0.2, M = 5, I = 100):
        dt = T/M
        #I Paths with M timesteps

        S = np.zeros(shape = (M+1, I))
        S[0] = S0

        for t in range(1, M+1):
            z = np.random.standard_normal(I)
            S[t] = S[t-1] * np.exp((r-0.5*sigma**2)*dt + sigma*math.sqrt(dt)*z)
        self.data = S
        return self
    
    def binning_t_fs(self, S_t, n):
        sorted = np.sort(S_t)
        return {f"bin{idx}": list(item) for idx, item in enumerate(list(zip_longest(*[iter(sorted)]*n, fillvalue="")))}

    def binning_t_kmeans(self, S_t, n):
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
                res[f"bin{i}"]=[S_t[0]]
        return res

    def binning(self, nbins=4, method="fixed"):
        _n = int(len(self.data[0])/nbins)
        res_dict = dict()
        #for every timestep
        for i in tqdm(range(self.data.shape[0]), desc=f"binning using {method}"):
            if method=="kmeans":
                res_dict[f"t{i}"] = self.binning_t_kmeans(self.data[i], n=nbins)
            elif method=="fixed":
                res_dict[f"t{i}"] = self.binning_t_fs(self.data[i], n=_n)
        self.bin_data = res_dict
        return self

    def create_edgelist(self, unique_edges=True):
        res_array = []

        for p in range(len(self.data[0])):
            res_array.append([])
            for i in range(len(self.data)):
                cur_t = self.bin_data[f"t{i}"]
                for b in cur_t.keys():
                    if min(cur_t[b]) <= self.data[i][p] <= max(cur_t[b]):
                        # Hier Statistik für Repräsentation der Bins angeben
                        res_array[p].append(np.median(cur_t[b]))
                        break

        res_array = np.array(res_array).T.tolist()
        edgelist = []
        for i in range(len(res_array)):
            try:
                for x, y in zip(res_array[i], res_array[i+1]):
                    counter = Counter(zip(res_array[i], res_array[i+1]))
                    s=0
                    for k in counter.keys():
                        if x==k[0]:
                            s += counter[k]
                    weight = counter[(float(x),float(y))]/s
                    edgelist.append({
                        "parent": x,
                        "child": y,
                        "par_value": x,
                        "ch_value": y,
                        "prob": weight,
                        "position_p": (i, x),
                        "position_c": (i+1, y)})
            except:
                pass

        if unique_edges:
            a = []
            for item in edgelist:
                if item not in a: a.append(item)
            self.edgelist =  pd.DataFrame.from_dict(a)
            return self
        
        self.edgelist = pd.DataFrame.from_dict(edgelist)

        return self
