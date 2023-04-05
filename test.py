# %%

import numpy as np
import pandas as pd 
import os
from datetime import datetime


from PythonFiles.DataStructures.Configuration import Configuration, getConfiguration

from PythonFiles.DataStructures.Variable import CategoricalVariable, DiscreteVariable

from PythonFiles.utils import convertByteToStr, convertToByteList, get_performance

# %%

def get_last_session(base_benchmark:str, algorithm:str):

    sessions = os.listdir(f"results/{algorithm}/{base_benchmark}")

    datetimes = [datetime.strptime(x[:-4], "%y-%m-%d_%H:%M:%S") for x in sessions]

    datetimes.sort()

    return pd.read_csv(f"results/{algorithm}/{base_benchmark}/{datetimes[-1].strftime('%y-%m-%d_%H:%M:%S')}.csv")

def get_conf_from_row(row):
    return getConfiguration(row["compression"].item(), 
                            row["Page Size"].item(), 
                            row["Cluster Size"].item(),
                            row["Cluster Bunch"].item())

def get_conf_from_benchmark(benchmark, algorithm):
    df = get_last_session(benchmark, algorithm)
    df_max = df[df["performance(%)"] == df["performance(%)"].max()]
    return get_conf_from_row(df_max)

conf_atlas = get_conf_from_benchmark("atlas", "annealer")
conf_lhcb = get_conf_from_benchmark("lhcb", "annealer")
conf_h1 = get_conf_from_benchmark("h1", "annealer")
conf_cms = get_conf_from_benchmark("cms", "annealer")


# %%

write_file: str = f'results/annealer/comparison.csv'
base_conf = Configuration() 
evaluations = 10
throughput_weight = 0.5

if not os.path.exists(write_file):

    with open(write_file, "w") as wf:
        wf.write("evaluated_benchmark,base_benchmark,")

        for name in base_conf.names:
            wf.write(f"{name},")

        wf.write(f"throughput(MB/s),size(MB),throughput_increase(%),size_decrease(%),performance(%),writing_time,processing_time")

        for i in range(evaluations):
            wf.write(f",res_{i}")

        wf.write("\n")

def determine_performance(confs: list[Configuration], base_benchmarks: list[str], evaluated_benchmark, test_file):
    base_results, _, _ = base_conf.evaluate(evaluated_benchmark, test_file, evaluations, folder="generated_base", remove=False)

    base_throughput, base_size, throughput_increase, size_decrease, base_performance = \
        get_performance(base_results, 0, 0, throughput_weight, is_base=True)

    for conf, base_benchmark in zip(confs, base_benchmarks):
        results, writing_time, processing_time = conf.evaluate(evaluated_benchmark, test_file)
        print(f"{results = }")

        mean_throughput, size, throughput_increase, size_decrease, performance = get_performance(results, base_throughput, base_size, throughput_weight)
        print(f"{performance = }")

        with open(write_file, "a") as wf:
            wf.write(f"{evaluated_benchmark},{base_benchmark},")
            for value in conf.values:
                wf.write(f"{value},")

            wf.write(f"{mean_throughput:.2f},{size},{throughput_increase:.3f},{size_decrease:.3f},{performance:.3f},{writing_time:.3f},{processing_time:.3f}")

            for res in results:
                wf.write(f",{res[0]:.1f}")

            wf.write("\n")

determine_performance([conf_atlas, conf_lhcb, conf_h1, conf_cms], ["atlas", "lhcb", "h1", "cms"], "atlas", "gg_data")
determine_performance([conf_atlas, conf_lhcb, conf_h1, conf_cms], ["atlas", "lhcb", "h1", "cms"], "lhcb", "B2HHH")
determine_performance([conf_atlas, conf_lhcb, conf_h1, conf_cms], ["atlas", "lhcb", "h1", "cms"], "h1", "h1dstX10")
determine_performance([conf_atlas, conf_lhcb, conf_h1, conf_cms], ["atlas", "lhcb", "h1", "cms"], "cms", "ttjet")
