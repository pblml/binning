from Simulation import *
from BinomialTree import *

sim_kmeans=Simulation().generate().binning(method="kmeans").create_edgelist()
sim_fixed=Simulation().generate().binning(method="fixed").create_edgelist()

tree = Tree().from_S(sim_fixed)
tree.calc_option_value(104, 0.9752, "p") #12.85 fixed 13.309 kmeans
tree.plot()
tree.from_S(sim_kmeans)
tree.calc_option_value(104, 0.9752, "p") #12.85 fixed 13.309 kmeans
tree.plot()

