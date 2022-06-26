from Simulation import *
from BinomialTree import *

sim = Simulation().generate()

sim_kmeans=sim.binning(method="kmeans").create_edgelist()
sim_fixed=sim.binning(method="fixed").create_edgelist()

tree = Tree().from_S(sim_kmeans)
tree_ex = Tree().from_edgelist("edgelist.csv")
tree_ex.calc_option_value(42, 0.9752, "p") #12.85 fixed 13.309 kmeans

tree_ex.plot()
