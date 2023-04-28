# %% 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PythonFiles.utils import convertByteToStr



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

df = df_h1

for c, s in df.groupby("compression"):

    plt.hist(s["performance(%)"], alpha=0.8, label=c)

plt.legend()
plt.show()


for c, s in df.groupby("compression"):
    print(c)
    print(f'Size \t\t=> mean: {s["size_decrease(%)"].mean():.3f}, min: {s["size_decrease(%)"].min():.3f}, max: {s["size_decrease(%)"].max():.3f}')
    print(f'througput \t=> mean: {s["throughput_increase(%)"].mean():.3f}, min: {s["throughput_increase(%)"].min():.3f}, max: {s["throughput_increase(%)"].max():.3f}')
    print(f'performance \t=> mean: {s["performance(%)"].mean():.3f}, min: {s["performance(%)"].min():.3f}, max: {s["performance(%)"].max():.3f}')
    print()

# %%



# %% 

import os

benchmark = "cms"

runs = []

for r in os.listdir(f"results/annealer/{benchmark}"):
    df = pd.read_csv(f"results/annealer/{benchmark}/{r}")

    df["algorithm"] = "annealer"
    df["session"] = r

    runs.append(df)

for r in os.listdir(f"results/annealer_multi_change/{benchmark}"):
    df = pd.read_csv(f"results/annealer_multi_change/{benchmark}/{r}")

    df["algorithm"] = "annealer_multi_change"
    df["session"] = r


    runs.append(df)


df_combined = pd.concat(runs)

df = df_combined

for c, s in df.groupby("compression"):
    plt.scatter(s["size_decrease(%)"], s["throughput_increase(%)"], label=c)


plt.xlabel("size decrease (%)")
plt.ylabel("throughput increase (%)")

plt.axhline(0, color="black", linestyle="dotted", alpha=0.5)
plt.axvline(0, color="black", linestyle="dotted", alpha=0.5)

plt.title(f"{benchmark}")
plt.legend(loc="lower center")
plt.show()

# %%

x_data = "Cluster Size"
y_data = "size_decrease(%)"

for g, s in df.groupby("compression"):
    plt.scatter(s[x_data], s[y_data])
    plt.title(g)
    plt.show()



# %%
from analyis_utils import plot_accepted, convertToMB, parameters

df_atlas = pd.read_csv("results/annealerv2/atlas/23-04-24_17:17:56.csv")
df_cms = pd.read_csv("results/annealerv2/cms/23-04-24_20:37:21.csv")
df_h1 = pd.read_csv("results/annealerv2/h1/23-04-25_06:00:19.csv")
df_lhcb = pd.read_csv("results/annealerv2/lhcb/23-04-25_09:39:58.csv")

df = df_lhcb

plot_accepted(df)



# %%

df.sort_values("performance(%)")[-10:][["performance(%)"] + parameters]

# %%

convertToMB(262144)
