# %%

from PythonFiles.DataStructures.Configuration import Configuration
from PythonFiles.Algorithms.Climber import Climber
from PythonFiles.Algorithms.Annealer import Annealer
from PythonFiles.Algorithms.AnnealerMultiBench import AnnealerMultiBench
from PythonFiles.Algorithms.AnnealerMultiChange import AnnealerMultiChange
import numpy as np
import matplotlib.pyplot as plt

# %%

def evolve_atlas(steps, evaluations):
    conf = Configuration()
    annealer = Annealer(conf,  benchmark_file="atlas", data_file="gg_data")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_cms(steps, evaluations):
    conf = Configuration()
    annealer = Annealer(conf,  benchmark_file="cms", data_file="ttjet")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_h1(steps, evaluations):
    conf = Configuration()
    annealer = Annealer(conf,  benchmark_file="h1", data_file="h1dstX10")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_lhcb(steps, evaluations):
    conf = Configuration()
    annealer = Annealer(conf,  benchmark_file="lhcb", data_file="B2HHH")
    annealer.evolve(steps=steps, evaluations=evaluations)

############################################################################################

def evolve_atlas_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiChange(conf,  benchmark_file="atlas", data_file="gg_data")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_cms_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiChange(conf,  benchmark_file="cms", data_file="ttjet")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_h1_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiChange(conf,  benchmark_file="h1", data_file="h1dstX10")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_lhcb_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiChange(conf,  benchmark_file="lhcb", data_file="B2HHH")
    annealer.evolve(steps=steps, evaluations=evaluations)


# evolve_atlas(100, 10)
# evolve_cms(100, 10)
# evolve_h1(100, 10)
# evolve_lhcb(100, 10)

# conf = Configuration()
# annealer = AnnealerMultiBench(conf)
# annealer.evolve(100, 20)

evolve_atlas_multi(100, 10)
# evolve_cms_multi(100, 10)
# evolve_h1_multi(100, 10)
# evolve_lhcb_multi(100, 10)

# evolve_atlas_multi(100, 10)
# evolve_cms_multi(100, 10)
# evolve_h1_multi(100, 10)
# evolve_lhcb_multi(100, 10)

