# %%

from Configuration import Configuration
from Climber import Climber
from Annealer import Annealer
import numpy as np
import matplotlib.pyplot as plt

# %%

conf = Configuration()
# annealer = Annealer(conf,  benchmark="atlas", data_file="gg_data")
annealer = Annealer(conf)


annealer.evolve(steps=100, evaluations=10)
