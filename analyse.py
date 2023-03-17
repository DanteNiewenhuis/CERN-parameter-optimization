# %% 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %%

df = pd.read_csv("results/annealer/23-03-17_12:21:38.csv")

# %%

accepted_performance = []

for i, s in df.iterrows():

    if s.success:
        accepted_performance.append(s.performance)
    
    else:
        accepted_performance.append(accepted_performance[-1])

# %%

plt.plot(accepted_performance)

plt.scatter(range(len(accepted_performance)), df.performance)

plt.show()

# %%

print(len(accepted_performance))