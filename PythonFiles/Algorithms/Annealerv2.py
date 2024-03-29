# %% 

# root [12] auto ntuple = ROOT::Experimental::RNTupleReader::Open("DecayTree" , "generated/B2HHH~none.ntuple")
# root [13] ntuple->PrintInfo(ROOT::Experimental::ENTupleInfo::kStorageDetails)

from dataclasses import dataclass
from datetime import datetime

from PythonFiles.DataStructures.Configuration import Configuration
import numpy as np
from random import random

from PythonFiles.utils import get_performance2


# %%

@dataclass
class Annealerv2:
    configuration: Configuration = None
    
    # benchmark definitions
    benchmark_file: str = "lhcb"
    data_file: str = "B2HHH"

    # Annealer parameters
    temperature_const: float = 2.5
    iteration: int = 0

    def get_temperature(self, iteration: int) -> float:
        """ Get temperature based on the current iteration

        Args:
            iteration (int)

        Returns:
            float
        """
        return self.temperature_const / np.log(iteration + 2)
    
    def get_probability(self, iteration:int, c:float) -> float:
        """ Get the probability of accepting a change based on 
        the current iteration and the difference in performance

        Args:
            iteration (int)
            c (float): The difference between the performance of 
                       the new and old configuration

        Returns:
            float
        """
        return np.exp(c/self.get_temperature(iteration))
    
    # Performance parameters
    throughput_weights: float = None
    base_throughput: float = None
    base_size: int = None
    performance: float = None

    def __post_init__(self):
        if self.configuration == None:
            self.configuration = Configuration()

    def step(self, iteration: int, evaluations: int = 10):
        """ Change the current configuration. 
            Determine the performance of the new configuration.
            Determine if you want to keep the new configuration.

        Args:
            iteration (int)
            evaluations (int, optional). Defaults to 10.
        """
        self.configuration.step()
        
        results, writing_time, processing_time = self.configuration.evaluate(self.benchmark_file, self.data_file, evaluations)

        print(f"{results = }")
        # Process the results to get performance measurements
        mean_throughput, size, mean_memory, throughput_increase, size_decrease, memory_decrease, performance = \
            get_performance2(results, self.base_throughput, self.base_size, self.base_memory, self.throughput_weights)
        
        print(f"{self.performance = }, {performance = }")
        
        # Determine if new configuration will be accepted
        c =  performance - self.performance 
        sucess = (c > 0) or (self.get_probability(iteration, c) > random())

        # Logging
        if sucess:
            self.log_step(results, mean_throughput, throughput_increase, size, size_decrease, mean_memory, memory_decrease, 
                          performance, True, writing_time, processing_time)
            self.performance = performance
        
        else:
            self.log_step(results, mean_throughput, throughput_increase, size, size_decrease, mean_memory, memory_decrease, 
                          performance, False, writing_time, processing_time)
            self.configuration.revert()
            

    def log_step(self, results: list[float], throughput:float, throughput_increase:float, size:int, 
                 size_decrease:float, memory:int, memory_decrease:float, performance: float = 1.0, accepted:bool = False, writing_time: int = 0, processing_time: int = 0):
        """ Log a taken step

        Args:
            results (list[float])
            throughput (float)
            throughput_increase (float)
            size (int)
            size_decrease (float)
            performance (float, optional): Defaults to 1.0.
            accepted (bool, optional): Defaults to False.
        """
        with open(self.write_file, "a") as wf:
            wf.write(f'{datetime.now().strftime("%y-%m-%d_%H:%M:%S")},')

            for value in self.configuration.values:
                wf.write(f"{value},")

            wf.write(f"{throughput:.2f},{size},{memory:.2f},{throughput_increase:.3f},{size_decrease:.3f},{memory_decrease:.3f},{performance:.3f},{accepted},{writing_time:.3f},{processing_time:.3f}")

            for res in results:
                wf.write(f",{res[0]:.1f}")
            for res in results:
                wf.write(f",{res[2]:.1f}")

            wf.write("\n")

    def get_base_performance(self, evaluations: int = 10):
        """ Get the performance of the "base" configuration. 
            This performance will be used to normalize all other results

        Args:
            evaluations (int, optional) Defaults to 10.
        """
        results, writing_time, processing_time = self.configuration.evaluate(self.benchmark_file, self.data_file, evaluations, folder="generated_base", remove=False)

        mean_throughput, size, mean_memory, throughput_increase, size_decrease, memory_decrease, performance = \
            get_performance2(results, 0, 0, 0, self.throughput_weights, is_base=True)

        self.base_throughput = mean_throughput
        self.base_size = size
        self.base_memory = mean_memory
        self.performance = performance

        self.log_step(results, mean_throughput, throughput_increase, size, size_decrease, mean_memory, memory_decrease, performance, True, writing_time, processing_time)

    def evolve(self, steps: int = 100, evaluations: int = 10):
        """ Evolve the current configuration using the simmulated annealing algorithm

        Args:
            steps (int, optional): Number of steps to evolve for. Defaults to 100.
            evaluations (int, optional): Number of times to run a benchmark with a configuration. Defaults to 10.
        """
        self.write_file: str = f'results/annealerv2/{self.benchmark_file}/{datetime.now().strftime("%y-%m-%d_%H:%M:%S")}.csv'
        
        with open(self.write_file, "w") as wf:
            wf.write("time,")

            for name in self.configuration.names:
                wf.write(f"{name},")

            wf.write(f"throughput(MB/s),size(MB),memory,throughput_increase(%),size_decrease(%),memory_decrease(%),performance(%),accepted,writing_time,processing_time")

            for i in range(evaluations):
                wf.write(f",throughput_{i}")
            for i in range(evaluations):
                wf.write(f",memory_{i}")

            wf.write("\n")

        # Log initial configuration
        print(f"Calculating Initial Performance")
        self.get_base_performance(evaluations)
        
        # evolve the configuration for the given number of steps
        print(f"Starting evolution")
        for i in range(steps):
            print(f"Step: {i} => Throughput: {self.performance:.3f}")
            self.step(i, evaluations)
