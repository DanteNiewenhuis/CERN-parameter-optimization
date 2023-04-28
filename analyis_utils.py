
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

parameters = ["compression", "Page Size", "Cluster Size", "Cluster Bunch"]
metrics = ["throughput(MB/s)", "size(MB)", "throughput_increase(%)", "size_decrease(%)", "performance(%)"]

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


def plot_accepted(df):

    res = []

    for index,row in df.iterrows():
        if row["accepted"]:
            res.append(row["performance(%)"])
        else:
            res.append(res[-1])

    plt.plot(res, label="accepted")
    plt.scatter(range(len(df)), df["performance(%)"], 
                color="red", sizes=[5 for _ in range(len(df))],
                label="attempted")

    plt.legend()

    plt.plot()
