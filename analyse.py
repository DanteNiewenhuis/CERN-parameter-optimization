# %% 

import numpy as np
import pandas as pd

# %%

df = pd.read_csv("results/23-03-14_16:56:15.csv")

# %%

df[df["success"] == 1]
