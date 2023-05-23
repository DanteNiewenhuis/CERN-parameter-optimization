# %%

from PythonFiles.DataStructures.Configuration import Configuration
from PythonFiles.Algorithms.Climber import Climber
from PythonFiles.Algorithms.Annealer import Annealer
from PythonFiles.Algorithms.Annealerv2 import Annealerv2
from PythonFiles.Algorithms.AnnealerMultiBench import AnnealerMultiBench
from PythonFiles.Algorithms.AnnealerMultiChange import AnnealerMultiChange
import numpy as np
import matplotlib.pyplot as plt

from PythonFiles.DataStructures.Variable import CategoricalVariable, DiscreteVariable
from PythonFiles.utils import convertByteToStr, convertToByteList

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
    annealer = AnnealerMultiBench(conf,  benchmark_file="atlas", data_file="gg_data")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_cms_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiBench(conf,  benchmark_file="cms", data_file="ttjet")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_h1_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiBench(conf,  benchmark_file="h1", data_file="h1dstX10")
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_lhcb_multi(steps, evaluations):
    conf = Configuration()
    annealer = AnnealerMultiBench(conf,  benchmark_file="lhcb", data_file="B2HHH")
    annealer.evolve(steps=steps, evaluations=evaluations)

############################################################################################

def get_conf_2():
    compression_var = CategoricalVariable("compression", ["lz4", "zstd"], current_idx=0)
    
    page_sizes = [(64,"KB"), (128,"KB"), (256,"KB"), (512,"KB"),
        (1,"MB"), (2,"MB"), (4,"MB"), (8,"MB"), (16,"MB")]
    page_size_var = DiscreteVariable("Page Size", convertToByteList(page_sizes), 
                                    value_names=convertByteToStr(page_sizes), current_idx=0)

    cluster_sizes = [(10, "MB"), (20,"MB"), (30,"MB"), (40,"MB"), (50,"MB"), (100,"MB"), (150,"MB")]
    cluster_size_var = DiscreteVariable("Cluster Size", convertToByteList(cluster_sizes), 
                                    value_names=convertByteToStr(cluster_sizes), current_idx=4)
    
    cluster_bunch_var = DiscreteVariable("Cluster Bunch", [1,2,3], current_idx=0)

    return Configuration(compression_var=compression_var, 
                         page_size_var=page_size_var,
                         cluster_size_var=cluster_size_var,
                         cluster_bunch_var=cluster_bunch_var
                         )




def evolve_atlas_2(steps, evaluations):
    conf = get_conf_2()
    annealer = Annealerv2(conf,  benchmark_file="atlas", data_file="gg_data", throughput_weights=[1/3, 1/3, 1/3])
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_cms_2(steps, evaluations):
    conf = get_conf_2()
    annealer = Annealerv2(conf,  benchmark_file="cms", data_file="ttjet", throughput_weights=[1/3, 1/3, 1/3])
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_h1_2(steps, evaluations):
    conf = get_conf_2()
    annealer = Annealerv2(conf,  benchmark_file="h1", data_file="h1dstX10", throughput_weights=[1/3, 1/3, 1/3])
    annealer.evolve(steps=steps, evaluations=evaluations)

def evolve_lhcb_2(steps, evaluations):
    conf = get_conf_2()
    annealer = Annealerv2(conf,  benchmark_file="lhcb", data_file="B2HHH", throughput_weights=[1/3, 1/3, 1/3])
    annealer.evolve(steps=steps, evaluations=evaluations)


# evolve_atlas(100, 10)
# evolve_cms(100, 10)
# evolve_h1(100, 10)
# evolve_lhcb(100, 10)

# conf = Configuration()
# annealer = AnnealerMultiBench(conf)
# annealer.evolve(100, 20)

# evolve_cms_multi(100, 20)
# evolve_atlas_multi(100, 20)
# evolve_lhcb_multi(100, 20)
# evolve_h1_multi(100, 20)

evolve_atlas_2(100, 20)
evolve_cms_2(100, 20)
evolve_h1_2(100, 20)
evolve_lhcb_2(100, 20)


