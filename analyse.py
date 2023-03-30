# %% 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %%

df = pd.read_csv("results/annealer/lhcb/23-03-17_15:22:54.csv")

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

df.columns

# %%

base_size = df['size'][0]

# %%

df['new_size'] = ((df['size'] - base_size) / base_size) * 100

# %%

df['new_size'].unique()