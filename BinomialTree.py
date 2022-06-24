import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class Node():

    def __init__(self, name, value, parents=[]):
        self.name = name
        self.value = value
        self.parents = parents
        #children dict of form {node: probability}
        self.children = {}
        self.ev = None

    def update_expvalue(self, strike, discount, opt, type):
        if len(self.children) > 0:
            s = discount*sum([child.ev*self.children[child] for child in self.children.keys()])
            self.ev = s
        else:
            if type in ["p", "put"]:
                self.ev = max(0.0, strike-self.value)
            elif type in ["c", "call"]:
                self.ev = max(0.0, self.value-strike)
        return self

    def add_parent(self, *kwargs):
        for parent, prob in kwargs:
            self.parents=list(self.parents)
            self.parents.append(parent)
            self.parents = list(set(self.parents))
            parent.children[self] = prob
        return self

    def __hash__(self):
        return hash(str(self.name))
    
    def __eq__(self, other):
        return(self.name == other.name and self.value == other.value)

    def __str__(self):
        return(f"Name: {self.name}\nValue: {self.value}\nParents: {self.parents}\nChildren: {self.children}\nExpected value: {self.ev}")

    def __repr__(self):
        return(self.name)
        
class Tree():

    def __init__(self, nodes=[]):
        self.nodes = self.append_node()

    def append_node(self, *kwargs):
        for n in kwargs:
            globals()[n].tree = self
            self.nodes.append(n)
        try:
            isinstance(self.nodes, list)
        except Exception as e:
            print(e)
            return []
        return self

    def from_edgelist(self, file):
        self.edgelist = pd.read_csv(file)
        all_nodes = set(pd.concat([self.edgelist["parent"], self.edgelist["child"]], axis=0))

        for idx, row in self.edgelist.iterrows():
            globals()[row["parent"]] = Node(row["parent"], row["par_value"])
            globals()[row["child"]] = Node(row["child"], row["ch_value"])

        for idx, row in self.edgelist.iterrows():
            # TODO: Get globals() out!
            globals()[row["child"]].add_parent((globals()[row["parent"]], row["prob"]))

        for node in all_nodes:
            self.append_node(node)

        return self

    def get_leafs(self):
        leafs = []
        for node in self.nodes:
            if len(globals()[node].children) == 0:
                leafs.append(node)
        return leafs

    def calc_price(self, strike, discount, type, opt="european"):
        parent_list = self.get_leafs()

        while len(parent_list) != 0:
            tmp_parent_list = []
            for node in parent_list:
                globals()[node].update_expvalue(strike, discount, opt, type)
                tmp_parent_list.extend([i.name for i in globals()[node].parents])
            parent_list=list(set(tmp_parent_list))
        return self

    def plot(self):
        G=nx.Graph()
        
        for node in self.nodes:
            t = int(node[-1])
            G.add_node(node, pos=(t, globals()[node].value), label=f"\n{globals()[node].value}\n{globals()[node].ev or ''}")
            for child in globals()[node].children:
                G.add_edge(node, child.name, label=globals()[node].children[child])
        
        nx.draw(G, pos=nx.get_node_attributes(G, 'pos'), with_labels = False)
        
        nx.draw_networkx_edge_labels(G, pos=nx.get_node_attributes(G, 'pos'),
            edge_labels=nx.get_edge_attributes(G,'label'))
        
        nx.draw_networkx_labels(G, pos=nx.get_node_attributes(G, 'pos'),
            labels=nx.get_node_attributes(G, 'label'))
        
        plt.show()
        
        return

    def __str__(self):
        return(str(self.edgelist))

edgelist = pd.read_csv("edgelist.csv")
tree = Tree()
tree.from_edgelist("edgelist.csv")
tree.plot()
print(tree.calc_price(42, 0.9753, type="p"))
tree.plot()