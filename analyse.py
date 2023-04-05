# %% 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PythonFiles.utils import convertByteToStr

def convertToMB(inp):
    return inp / 1_048_576


def increase_to_decrease(path_to_df):
    df = pd.read_csv(path_to_df)

    print(df.columns)
    if 'size_decrease(%)' in list(df.columns):
        print("skip")
        return

    df['size_decrease(%)'] = -df['size_increase(%)']

    new_columns = ['compression', 'Page Size', 'Cluster Size', 'Cluster Bunch',
        'throughput(MB/s)', 'size(MB)', 'throughput_increase(%)',
        'size_decrease(%)', 'performance(%)', 'accepted', 'res_0', 'res_1',
        'res_2', 'res_3', 'res_4', 'res_5', 'res_6', 'res_7', 'res_8', 'res_9']

    df.to_csv(path_to_df, columns=new_columns, index=False)

# import os

# for bench in os.listdir("results/annealer"):
#     for run in os.listdir(f"results/annealer/{bench}"):
#         increase_to_decrease(f"results/annealer/{bench}/{run}")


# %%


df_atlas = pd.read_csv("results/annealer/atlas/23-04-05_04:26:00.csv")
df_lhcb = pd.read_csv("results/annealer/lhcb/23-03-30_18:53:38.csv")
df_h1 = pd.read_csv("results/annealer/h1/23-04-05_07:50:05.csv")
df_cms = pd.read_csv("results/annealer/cms/23-04-04_16:56:45.csv")

# %%

df = df_cms

# %%

df = df.sort_values("performance(%)")
df[df["performance(%)"] > 65]

# %%


plt.hist(df["size_decrease(%)"], alpha=0.8, bins=20, label="size")
plt.hist(df["throughput_increase(%)"], alpha=0.8, bins=20, label="throughput")
plt.hist(df["performance(%)"], alpha=0.8, bins=20, label="performance")

plt.legend()
plt.show()

# %%

for c, s in df.groupby("compression"):
    print(c)
    print(f'Size \t\t=> mean: {s["size_decrease(%)"].mean():.3f}, min: {s["size_decrease(%)"].min():.3f}, max: {s["size_decrease(%)"].max():.3f}')
    print(f'througput \t=> mean: {s["throughput_increase(%)"].mean():.3f}, min: {s["throughput_increase(%)"].min():.3f}, max: {s["throughput_increase(%)"].max():.3f}')
    print(f'performance \t=> mean: {s["performance(%)"].mean():.3f}, min: {s["performance(%)"].min():.3f}, max: {s["performance(%)"].max():.3f}')
    print()

# %%


# %%
