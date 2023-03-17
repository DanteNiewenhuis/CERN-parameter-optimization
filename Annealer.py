# %% 

# root [12] auto ntuple = ROOT::Experimental::RNTupleReader::Open("DecayTree" , "generated/B2HHH~none.ntuple")
# root [13] ntuple->PrintInfo(ROOT::Experimental::ENTupleInfo::kStorageDetails)

from dataclasses import dataclass
from tqdm import tqdm
from datetime import datetime
import os

from Configuration import Configuration
import numpy as np
from random import random

from utils import run_benchmark, generate_file


# %%

@dataclass
class Annealer:
    configuration: Configuration = None
    benchmark: str = "lhcb"
    data_file: str = "B2HHH"
    temperature: float = 0.05
    alpha: float = 0.9
    throughput_weight: float = 0.5

    base_throughput: float = None
    base_size: int = None
    performance: float = None

    def __post_init__(self):
        if self.configuration == None:
            self.configuration = Configuration()

    def evaluate_configuration(self, conf:Configuration, evaluations: int = 10) -> list[float]:
        
        print(f"Evaluating configuration:\n {str(conf)}")

        output_file = generate_file(conf, self.benchmark, self.data_file)
        
        results = []
        for _ in tqdm(range(evaluations)):
            res, out = run_benchmark(conf, self.benchmark, self.data_file)
            if res == None:
                raise ValueError(f"run_benchmark resulted in None: {out = }")
            results.append(res)

        return results, output_file

    def step(self, evaluations: int = 10):
        self.configuration.step()
        
        results, output_file = self.evaluate_configuration(self.configuration, evaluations)

        print(f"{results = }")
        _throughput = np.mean(results)
        _size = os.stat(output_file).st_size

        _relative_throughput = _throughput / self.base_throughput
        _relative_size = _size / self.base_size

        _performance = self.throughput_weight * _relative_throughput - \
                       (1-self.throughput_weight) * _relative_size

        print(f"{self.performance = }, {_performance = }")
        c =  _performance - self.performance

        sucess = (c > 0) or (np.exp(c/self.temperature) > random())

        if sucess:
            self.log_step(results, _throughput, _relative_throughput, _size, _relative_size, _performance, True)
            self.performance = _performance
        
        else:
            self.log_step(results, _throughput, _relative_throughput, _size, _relative_size, _performance, False)
            self.configuration.revert()
            

    def log_step(self, results, throughput:float, relative_throughput:float, size:int, 
                 relative_size:float, performance: float = 1.0, success:bool = False):
        with open(self.write_file, "a") as wf:
            for value in self.configuration.values:
                wf.write(f"{value},")

            wf.write(f"{throughput:.2f},{relative_throughput:.2f},{size},{relative_size:.2f},{performance},{success}")

            for res in results:
                wf.write(f",{res:.1f}")

            wf.write("\n")

    def get_base_performance(self, conf: Configuration, evaluations: int = 10):
        results, output_file = self.evaluate_configuration(self.configuration, evaluations)

        self.base_throughput = np.mean(results)
        self.base_size = os.stat(output_file).st_size

        self.performance = 0.0
        self.log_step(results, self.base_throughput, 1, self.base_size, 1, self.performance, True)

    def evolve(self, steps: int = 100, evaluations: int = 10):
        self.write_file: str = f'results/annealer/{self.benchmark}/{datetime.now().strftime("%y-%m-%d_%H:%M:%S")}.csv'
        
        with open(self.write_file, "w") as wf:
            for name in self.configuration.names:
                wf.write(f"{name},")

            wf.write(f"throughput,relative_throughput,size,relative_size,performance,success")

            for i in range(evaluations):
                wf.write(f",res_{i}")

            wf.write("\n")

        # Log initial configuration
        print(f"Calculating Initial Performance")
        self.get_base_performance(self.configuration, evaluations)
        
        # evolve the configuration for the given number of steps
        print(f"Starting evolution")
        for i in range(steps):
            print(f"Step: {i} => Throughput: {self.performance:.3f}")
            self.step(evaluations)