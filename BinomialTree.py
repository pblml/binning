import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from Simulation import *
import re

class Node():

    def __init__(self, name, value, t=None, parents=[]):
        self.name = name
        self.value = value
        self.t = self.set_t(t)
        self.parents = parents
        #children dict of form {node: probability}
        self.children = {}
        self.ev = ""

    def get_option_value(self, strike, discount, opt, type):
        """
        Calculate the option value of a node

        self: Node object
        strike: Strike price of the option
        discount factor: discount factor
        opt: "put" or "call"
        type: "european" or "american"
        """

        if len(self.children) > 0:
            s = discount*sum([child.ev*self.children[child] for child in self.children.keys()])
            exercise_value = (strike-self.value) if type in ["p", "put"] else (self.value-strike)
            self.ev = max(s, exercise_value) if opt == "american" else s
        else:
            if type in ["p", "put"]:
                self.ev = max(0.0, strike-self.value)
            elif type in ["c", "call"]:
                self.ev = max(0.0, self.value-strike)
        return self

    def add_parent(self, *kwargs):
        """
        Method to add parents to a node
        self: Node object to append to.
        *kwargs: parent node given as a tuple of (parent_node, probability)
        """

        for parent, prob in kwargs:
            self.parents=list(self.parents)
            self.parents.append(parent)
            self.parents = list(set(self.parents))
            parent.children[self] = prob

        return self

    def set_t(self, t):
        """
        Set the time period for a node

        Sets the time period when a node gets initialized. If the Nodes `name`-attribute contains a 't[0-9]'-string
        it is used to set the time

        self: Node object
        t: hard coded t
        """

        if re.search("t[0-9]+", str(self.name)):
            return int(self.name[-1])
        else:
           return t

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
        self.nodes = []
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

    def from_S(self, S):
        self.nodes = [] #clear old node list
        self.edgelist = S.edgelist # get the edgelist attribute of the Simulation object

        # get a list of all nodes in S
        all_nodes = set(pd.concat([self.edgelist["parent"], self.edgelist["child"]], axis=0))

        # create node for every parent and child in S.edgelist
        for idx, row in self.edgelist.iterrows():
            globals()[row["parent"]] = Node(row["parent"], row["par_value"], row["position_p"][0])
            globals()[row["child"]] = Node(row["child"], row["ch_value"], row["position_c"][0])

        # add the parents to each node
        for idx, row in self.edgelist.iterrows():
            # TODO: Get globals() out!
            globals()[row["child"]].add_parent((globals()[row["parent"]], row["prob"]))

        # append all nodes to the tree
        for node in all_nodes:
            self.append_node(node)

        return self

    def get_leafs(self):
        """
        Helper method to get the leafs of the Tree.
        
        Used to find the starting point of the `calc_options_value`

        """

        leafs = []
        for node in self.nodes:
            if len(globals()[node].children) == 0:
                leafs.append(node)
        return leafs

    def calc_option_value(self, strike, discount, type, opt="european"):
        parent_list = self.get_leafs()

        while len(parent_list) != 0:
            tmp_parent_list = []
            for node in parent_list:
                globals()[node].get_option_value(strike, discount, opt, type)
                tmp_parent_list.extend([i.name for i in globals()[node].parents])
            parent_list=list(set(tmp_parent_list))
        return self

    def plot(self):
        """
        Generate the plot of the Tree() object using its `nodes` attribute.
        If `calc_option_value()` was executed on the tree, it also shows the option value for each node.
        """

        # initialize Graph object
        G=nx.Graph()
        
        for node in self.nodes:
            G.add_node(node, pos=(globals()[node].t, globals()[node].value), label=f"{round(globals()[node].value, 2)}\n{round(globals()[node].ev, 2)}")
            for child in globals()[node].children:
                G.add_edge(node, child.name, label=round(globals()[node].children[child], 2))
        
        nx.draw(G, pos=nx.get_node_attributes(G, 'pos'), with_labels = False)

        nx.draw_networkx_edge_labels(G, pos=nx.get_node_attributes(G, 'pos'), label_pos=0.3,
            edge_labels=nx.get_edge_attributes(G,'label'))
        
        nx.draw_networkx_labels(G, pos=nx.get_node_attributes(G, 'pos'),
            labels=nx.get_node_attributes(G, 'label'))

        #annotation_text_x = max([i for i in nx.get_node_attributes(G, 'pos')])
        # plt.text(0, annotation_text_x, "Annotation")
        
        plt.show()
        
        return

    def __str__(self):
        return(str(self.edgelist))
