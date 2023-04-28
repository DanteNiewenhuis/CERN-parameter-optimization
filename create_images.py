# %%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


from PythonFiles.utils import convertByteToStr


def get_accepted(df, column:str):
    res = []

    for index,row in df.iterrows():
        if (row["accepted"]):
            res.append(row[column])
        else:
            res.append(res[-1])

    return res

# %%
##########################################################################
# Temperature
##########################################################################

def get_temp(d, i):
    return d/np.log(i+2)

temp = [get_temp(3, i) for i in range(100)]


plt.plot(temp)
plt.ylabel("Temperature")
plt.xlabel("Iteration")
plt.tight_layout()
plt.savefig("Images/temperature.png")


# %%
##########################################################################
# Probability
##########################################################################

def get_prob(d, c, i):
    return np.exp(c/get_temp(d, i))

d = 3
c = -1

temp = [get_prob(d, c, i) for i in range(100)]


plt.plot(temp)
plt.ylabel("Probability")
plt.xlabel("Iteration")
plt.tight_layout()
plt.savefig("Images/annealer_prob.png")

# %%
##########################################################################
# Multiple benchmarks
##########################################################################


df = pd.read_csv("results/annealer_multi_bench/23-04-12_16:37:14.csv")

performances = ["performance_atlas(%)", "performance_cms(%)", "performance_h1(%)", "performance_lhcb(%)"]
parameters = ["compression", "Cluster Size", "Page Size", "Cluster Bunch"]


df_comp = pd.read_csv("results/annealer/comparison.csv")

perf = get_accepted(df, "performance(%)")
perf_atlas = get_accepted(df, "performance_atlas(%)")
perf_cms = get_accepted(df, "performance_cms(%)")
perf_h1 = get_accepted(df, "performance_h1(%)")
perf_lhcb = get_accepted(df, "performance_lhcb(%)")


plt.plot(perf, label="mean", linewidth=3)
plt.plot(perf_atlas, label="atlas", linestyle=(0,(1,1)))
plt.plot(perf_cms, label="cms", linestyle=(0,(1,1)))
plt.plot(perf_h1, label="h1", linestyle=(0,(1,1)))
plt.plot(perf_lhcb, label="lhcb", linestyle=(0,(1,1)))

plt.xlabel("Iteration")
plt.ylabel("Performance(%)")

plt.legend()

plt.tight_layout()
plt.savefig("Images/combined_annealer.png")


# %%
##########################################################################
# Exploration
##########################################################################

def combine_df(benchmark):

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


    return pd.concat(runs)


for benchmark in ["atlas", "cms", "h1", "lhcb"]:
    print(benchmark)
    df = combine_df(benchmark)

    for c, s in df.groupby("compression"):
        plt.scatter(s["size_decrease(%)"], s["throughput_increase(%)"], label=c)


    plt.xlabel("size decrease (%)")
    plt.ylabel("throughput increase (%)")

    plt.axhline(0, color="black", linestyle="dotted", alpha=0.5)
    plt.axvline(0, color="black", linestyle="dotted", alpha=0.5)

    plt.title(f"{benchmark}")
    plt.legend(loc="lower center")
    plt.tight_layout()
    plt.savefig(f"Images/pareto_front_{benchmark}")
    plt.cla()

# %%

benchmark = "cms"
parameter = "Cluster Bunch"
df = combine_df(benchmark)

for g, s in df.groupby("compression"):
    print(g)
    # if g != "none":
    #     continue
    plt.scatter(s[parameter], s["performance(%)"])
    plt.xlabel(parameter)
    plt.ylabel("throughput_increase(%)")
    plt.title(f"{parameter} {benchmark}")
    plt.tight_layout()
    plt.savefig(f"Images/{benchmark}_{g}_{parameter}")
    plt.show()