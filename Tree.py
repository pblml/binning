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

        Parameters
        ----------
        
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

        Parameters
        ----------
        self:
            Node object to append to
        *kwargs:
            Parent node given as a tuple of (parent_node, probability)
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

        Parameters
        ----------
        self: Node object
        t: int
            hard coded t
        """

        if re.search("t[0-9]+", str(self.name)):
            # TODO: regex extraction instead of using last character of `self.name`
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
        self.option_params = None

    def append_node(self, *kwargs):
        """
        Append an arbitrary number of nodes to the tree.

        Parameters
        ----------
        *kwargs: Node object
            `Node` object to append to the tree.
        """
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
        """
        Create a Tree from a .csv file.
        Mostly used for testing purposes.

        Parameters
        ----------
        file: string
            Path to csv file. Format should match the following example:\n
            `parent,par_value,child,ch_value,prob`\n
            `b0t0,40,b0t1,34.72,0.4461`
        
        """
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
        """
        Create a Tree from a `Simulation` object.

        Parameters
        ----------
        S: Simulation object
            Simulation object on which `generate` and `binning` was executed

        """
        self.nodes = [] #clear old node list
        self.edgelist = S.edgelist # get the edgelist attribute of the Simulation object

        # get a list of all nodes in S
        all_nodes = set(pd.concat([self.edgelist["parent"], self.edgelist["child"]], axis=0))

        # create node for every parent and child in S.edgelist
        for idx, row in self.edgelist.iterrows():
            globals()[row["parent"]] = Node(row["parent"], row["par_value"], row["position_p"][0])
            globals()[row["child"]] = Node(row["child"], row["ch_value"], row["position_c"][0])

        # add the parents to each node
        for _, row in self.edgelist.iterrows():
            # TODO: Get globals() out!
            globals()[row["child"]].add_parent((globals()[row["parent"]], row["prob"]))

        # append all nodes to the tree
        for node in all_nodes:
            self.append_node(node)

        return self

    def get_leafs(self):
        """
        Helper method to get the leafs of the Tree.
        
        Used to find the starting point of the `calc_options_value` method.
        
        Returns
        -------
        list
            List of leaf nodes
        """

        leafs = []
        for node in self.nodes:
            if len(globals()[node].children) == 0:
                leafs.append(node)
        return leafs

    def calc_option_value(self, strike, discount, type="call", opt="european"):
        """
        Calculation of option values for all nodes in the tree.

        Parameters
        ----------
        self: Tree Object
        strike: float
            Strike price of the option
        discount: float
            discount factor calculated by `exp(-`
        type: {"call", "put"}
        opt: {"european", "american"}
        """
        self.option_params = {"Strike Price": strike, "Discount Rate": discount, "Type": type, "Option": opt}
        #get the leafs to start calculation
        parent_list = self.get_leafs()

        # while the parent list is not empty...
        while len(parent_list) != 0:
            tmp_parent_list = [] # initialize list for parents of currently calculating nodes
            for node in parent_list:
                globals()[node].get_option_value(strike, discount, opt, type)
                tmp_ev = globals()[node].ev
                tmp_parent_list.extend([i.name for i in globals()[node].parents])
            parent_list=list(set(tmp_parent_list)) # set the previous timesteps nodes as the new parent_list
        self.option_price = tmp_ev
        return self

    def plot(self):
        """
        Generate and show the plot of the Tree() object using its `nodes` attribute.

        If `calc_option_value()` was executed on the tree, it also shows the option value for each node.

        Returns
        -------
            None
        """

        # initialize Graph object
        G=nx.Graph()
        
        for node in self.nodes:
            G.add_node(node, pos=(globals()[node].t, globals()[node].value), label=f"{round(globals()[node].value, 2)}\n{round(globals()[node].ev, 2)}")
            for child in globals()[node].children:
                G.add_edge(node, child.name, label=round(globals()[node].children[child], 2))
        
        # Draw graph without nodes and labels
        nx.draw(G,
            pos=nx.get_node_attributes(G, 'pos'),
            with_labels=False,
            node_size=0)

        # Draw edge labels
        nx.draw_networkx_edge_labels(G,
            pos=nx.get_node_attributes(G, 'pos'),
            label_pos=0.3,
            edge_labels=nx.get_edge_attributes(G,'label'))
        
        # Draw Node labels with a bounding box
        nx.draw_networkx_labels(G,
            pos=nx.get_node_attributes(G, 'pos'),
            bbox=dict(facecolor="white"),
            labels=nx.get_node_attributes(G, 'label'))
        
        # if there theres an option calculated on the tree, draw annotation with information
        # about the option
        if self.option_params is not None:
            annotation_text_x = max([globals()[node].value for node in self.nodes])-\
                max([globals()[node].value for node in self.nodes])*0.05
            plt.text(0, annotation_text_x,
                "\n".join([f"{key}: {value}" for key, value in self.option_params.items()])
                )
        
        plt.show()
        
        return
 
    def __str__(self):
        return(str(self.edgelist))
