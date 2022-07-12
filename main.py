from Simulation import *
from Tree import *

# Simulation der Werte mit den Standardparametern

sim_kmeans=Simulation().generate().binning(method="kmeans", nbins=3).create_edgelist()
sim_fixed=Simulation().generate().binning(method="fixed", nbins=3).create_edgelist()

# Initialisieren des Baums mit den Simulationsobjekten
tree = Tree().from_S(sim_fixed)
tree.calc_option_value(104, 0.9752, "c")
tree.plot()

tree.from_S(sim_kmeans)
tree.calc_option_value(104, 0.9752, "c")
tree.plot()

# Initialisieren des Baums mittels einer Liste von Kanten
tree.from_edgelist("edgelist.csv")

tree.calc_option_value(42, 0.9752, "p", opt="american")
tree.plot()

tree.calc_option_value(42, 0.9752, "p", opt="european")
tree.plot()