# %% 

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

# %%

df = pd.read_csv("results/annealer_multi_bench/23-04-12_16:37:14.csv")

performances = ["performance_atlas(%)", "performance_cms(%)", "performance_h1(%)", "performance_lhcb(%)"]
parameters = ["compression", "Cluster Size", "Page Size", "Cluster Bunch"]


df_comp = pd.read_csv("results/annealer/comparison.csv")

def get_accepted(df, column:str):
    res = []

    for index,row in df.iterrows():
        if (row["accepted"]):
            res.append(row[column])
        else:
            res.append(res[-1])

    return res

# %%

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

plt.legend()

plt.show()

# %%

for name, rows in df_comp.groupby("base_benchmark"):
    print(f"{name = } => mean = {rows['performance(%)'].mean()}")

# %%

df_comp[df_comp["base_benchmark"] == "atlas"][["evaluated_benchmark", "performance(%)"]]

# %%

def cross_table(df, benchmarks):
    grid = [[""] + [bench for bench in benchmarks]]
    
    for base_benchmark in benchmarks:
        row = [base_benchmark]
        for evaluated_benchmark in benchmarks:
            s = df[(df["base_benchmark"] == base_benchmark) & 
                   (df["evaluated_benchmark"] == evaluated_benchmark)]

            row.append(s["performance(%)"].item())

        grid.append(row)

    return grid

table = cross_table(df_comp, ["atlas", "cms", "h1", "lhcb"])

# %%

df_accepted = df[df["accepted"] == True]

df_accepted[performances + parameters]

# %%

s = ""
for row in table:
    s += " & ".join([str(x) for x in row]) + "\\\\\hline\n"

print(s)
# %%
