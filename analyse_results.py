# %%

import numpy as np
import pandas as pd 

from analyis_utils import get_all_results

import matplotlib.pyplot as plt

# %%


df = get_all_results("lhcb")

df_sorted = df.sort_values("performance(%)", ascending=False)

df_zstd = df_sorted[df_sorted["compression"] == "zstd"]
df_lz4 = df_sorted[df_sorted["compression"] == "lz4"]
other_parameters = ["Page Size", "Cluster Size", "Cluster Bunch"]


# %%

def measure_variable_effect(df: pd.DataFrame, variable: str):
    print(df[variable].value_counts())

    df = df.sort_values(variable)

    var_values = []
    mins = []
    maxs = []
    means = []
    stds = []

    for g, r in df.groupby(variable):
        var_values.append(int(g))
        mins.append(r['performance(%)'].min())
        maxs.append(r['performance(%)'].max())
        means.append(r['performance(%)'].mean())
        stds.append(r['performance(%)'].std())
    
    plot_names = ["min", "max", "mean", "std"]

    values = [mins, maxs, means]

    fig, ax = plt.subplots(len(values))
    
    fig.suptitle(f"{variable}")
    
    for i, (val, name) in enumerate(zip(values, plot_names)):
        ax[i].plot(var_values, val)
        ax[i].set_title(f"{name}")

    fig.set_figheight(8)
    fig.tight_layout()
    plt.show()

measure_variable_effect(df_zstd, "Page Size")


# %%

def get_rows(df, compression, page_size, cluster_size, cluster_bunch):
    return df[(df["compression"] == compression) &
              (df["Page Size"] == page_size) &
              (df["Cluster Size"] == cluster_size) &
              (df["Cluster Bunch"] == cluster_bunch)]

def compare_to_best(df, rows):
    max_performance = df["performance(%)"].max()

    row_performance = rows["performance(%)"].max()

    return (row_performance / max_performance) * 100

first_compr = "zstd"
second_compr = "lz4"

first_df = df[df["compression"] == first_compr].sort_values("performance(%)", ascending=False)
second_df = df[df["compression"] == second_compr].sort_values("performance(%)", ascending=False)

for i in range(10):
    page_size, cluster_size, cluster_bunch = first_df.iloc[i][other_parameters]
    
    rows = get_rows(df, second_compr, page_size, cluster_size, cluster_bunch)
    
    print(f"{i = } performance: {compare_to_best(second_df, rows)}")

# %%

first_df[:10][other_parameters]