# %% 

# root [12] auto ntuple = ROOT::Experimental::RNTupleReader::Open("DecayTree" , "generated/B2HHH~none.ntuple")
# root [13] ntuple->PrintInfo(ROOT::Experimental::ENTupleInfo::kStorageDetails)

from dataclasses import dataclass
from datetime import datetime

from PythonFiles.DataStructures.Configuration import Configuration
import numpy as np
from random import random

from PythonFiles.utils import get_performance


# %%

@dataclass
class AnnealerMultiChange:
    configuration: Configuration = None
    
    # benchmark definitions
    benchmark_file: str = "lhcb"
    data_file: str = "B2HHH"

    # Annealer parameters
    temperature_const: float = 3
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
    throughput_weights: float = [0.5, 0.5]
    base_throughput: float = None
    base_size: int = None
    performance: float = None

    change_probabilities = []

    def __post_init__(self):
        if self.configuration == None:
            self.configuration = Configuration()

    def create_probability_list(self, iterations):
        x = np.arange(len(self.configuration.variables)) + 1
        prop = x[::-1] / np.sum(x)
        last_prop = np.zeros(len(self.configuration.variables))
        last_prop[0] = 1

        self.change_probabilities = np.linspace(prop, last_prop, iterations)

    def get_num_changes(self, iteration):
        if iteration > len(self.change_probabilities):
            return self.change_probabilities[-1]
        
        return self.change_probabilities[iteration]

    def step(self, iteration: int, evaluations: int = 10):
        """ Change the current configuration. 
            Determine the performance of the new configuration.
            Determine if you want to keep the new configuration.

        Args:
            iteration (int)
            evaluations (int, optional). Defaults to 10.
        """
        # print(f"{iteration = }, {self.get_num_changes(iteration) = }")

        num_changes = self.configuration.step_multi(self.get_num_changes(iteration))

        results, writing_time, processing_time = self.configuration.evaluate(self.benchmark_file, self.data_file, evaluations)

        print(f"{results = }")
        # Process the results to get performance measurements
        mean_throughput, size, throughput_increase, size_decrease, performance = \
            get_performance(results, self.base_throughput, self.base_size, self.throughput_weight)
        
        print(f"{self.performance = }, {performance = }")
        
        # Determine if new configuration will be accepted
        c =  performance - self.performance 
        sucess = (c > 0) or (self.get_probability(iteration, c) > random())

        # Logging
        if sucess:
            self.log_step(num_changes, results, mean_throughput, throughput_increase, size, size_decrease, performance, True, writing_time, processing_time)
            self.performance = performance
        
        else:
            self.log_step(num_changes, results, mean_throughput, throughput_increase, size, size_decrease, performance, False, writing_time, processing_time)
            self.configuration.revert_multi()
            

    def log_step(self, num_changes: int, results: list[float], throughput:float, throughput_increase:float, size:int, 
                 size_decrease:float, performance: float = 1.0, accepted:bool = False, writing_time: int = 0, processing_time: int = 0):
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
            wf.write(f'{datetime.now().strftime("%y-%m-%d_%H:%M:%S")},{num_changes},')

            for value in self.configuration.values:
                wf.write(f"{value},")

            wf.write(f"{throughput:.2f},{size},{throughput_increase:.3f},{size_decrease:.3f},{performance:.3f},{accepted},{writing_time:.3f},{processing_time:.3f}")

            for res in results:
                wf.write(f",{res[0]:.1f}")

            wf.write("\n")

    def get_base_performance(self, evaluations: int = 10):
        """ Get the performance of the "base" configuration. 
            This performance will be used to normalize all other results

        Args:
            evaluations (int, optional) Defaults to 10.
        """
        results, writing_time, processing_time = self.configuration.evaluate(self.benchmark_file, self.data_file, evaluations, folder="generated_base", remove=False)

        mean_throughput, size, throughput_increase, size_decrease, performance = \
            get_performance(results, 0, 0, self.throughput_weights, is_base=True)

        self.base_throughput = mean_throughput
        self.base_size = size
        self.performance = performance

        self.log_step(0, results, mean_throughput, throughput_increase, size, size_decrease, performance, True, writing_time, processing_time)

    def evolve(self, steps: int = 100, evaluations: int = 10):
        """ Evolve the current configuration using the simmulated annealing algorithm

        Args:
            steps (int, optional): Number of steps to evolve for. Defaults to 100.
            evaluations (int, optional): Number of times to run a benchmark with a configuration. Defaults to 10.
        """
        self.write_file: str = f'results/annealer_multi_change/{self.benchmark_file}/{datetime.now().strftime("%y-%m-%d_%H:%M:%S")}.csv'
        
        with open(self.write_file, "w") as wf:
            wf.write("time,number_of_changes,")
            for name in self.configuration.names:
                wf.write(f"{name},")

            wf.write(f"throughput(MB/s),size(MB),throughput_increase(%),size_decrease(%),performance(%),accepted,writing_time,processing_time")

            for i in range(evaluations):
                wf.write(f",res_{i}")

            wf.write("\n")

        self.create_probability_list(steps*2)

        # Log initial configuration
        print(f"Calculating Initial Performance")
        self.get_base_performance(evaluations)
        
        # evolve the configuration for the given number of steps
        print(f"Starting evolution")
        for i in range(steps):
            print(f"Step: {i} => Throughput: {self.performance:.3f}")
            self.step(i, evaluations)
