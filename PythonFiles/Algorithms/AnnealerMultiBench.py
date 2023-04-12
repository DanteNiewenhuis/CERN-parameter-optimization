# %% 

# root [12] auto ntuple = ROOT::Experimental::RNTupleReader::Open("DecayTree" , "generated/B2HHH~none.ntuple")
# root [13] ntuple->PrintInfo(ROOT::Experimental::ENTupleInfo::kStorageDetails)

from dataclasses import dataclass, field
from datetime import datetime

from PythonFiles.DataStructures.Configuration import Configuration
import numpy as np
from random import random

from PythonFiles.utils import get_performance

# %%

@dataclass
class AnnealerMultiBench:
    configuration: Configuration = None
    
    # benchmark definitions
    benchmark_files: list[str] = field(default_factory=lambda: ["atlas", "cms", "h1", "lhcb"])
    data_files: list[str] = field(default_factory=lambda: ["gg_data", "ttjet", "h1dstX10", "B2HHH"])

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
    throughput_weight: float = 0.5
    base_throughputs: list[float] = field(default_factory=list)
    base_sizes: list[int] = field(default_factory=list)
    current_performance: float = field(default_factory=list)

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

        result_list = []
        writing_times = []
        processing_times = []

        mean_throughputs = []
        sizes = []
        throughput_increases = []
        size_decreases = []
        performances = []

        for bench, data_file, base_throughput, base_size in zip(self.benchmark_files, self.data_files, self.base_throughputs, self.base_sizes):
        
            results, writing_time, processing_time = self.configuration.evaluate(bench, data_file, evaluations)

            result_list.append(results)
            writing_times.append(writing_time)
            processing_times.append(processing_time)

            print(f"{results = }")
            # Process the results to get performance measurements
            mean_throughput, size, throughput_increase, size_decrease, performance = \
                get_performance(results, base_throughput, base_size, self.throughput_weight)
            
            mean_throughputs.append(mean_throughput)
            sizes.append(size)

            throughput_increases.append(throughput_increase)
            size_decreases.append(size_decrease)

            performances.append(performance)


        new_performance = np.mean(performances)

        print(f"{self.current_performance = }, {new_performance = }")
        
        # Determine if new configuration will be accepted
        c =  new_performance - self.current_performance 
        sucess = (c > 0) or (self.get_probability(iteration, c) > random())

        # Logging
        if sucess:
            self.log_step(result_list, mean_throughputs, throughput_increases, sizes, size_decreases, performances, new_performance, True, writing_times, processing_times)
            self.current_performance = new_performance
        
        else:
            self.log_step(result_list, mean_throughputs, throughput_increases, sizes, size_decreases, performances, new_performance, False, writing_times, processing_times)
            self.configuration.revert()
            

    def log_step(self, result_list: list[list[float]], throughputs:list[float], throughput_increases:list[float], sizes:list[int], 
                 size_decreases:list[float], performances: list[float], performance: float = 0.0, accepted:bool = False, 
                 writing_times: list[int] = 0, processing_times: list[int] = 0):
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
            for value in self.configuration.values:
                wf.write(f"{value},")

            for i in range(len(result_list)):
                wf.write(f"{throughputs[i]:.3f},")
            for i in range(len(result_list)):
                wf.write(f"{sizes[i]},")
            for i in range(len(result_list)):
                wf.write(f"{writing_times[i]:.3f},")
            for i in range(len(result_list)):
                wf.write(f"{processing_times[i]:.3f},")
            for i in range(len(result_list)):
                wf.write(f"{throughput_increases[i]:.3f},")
            for i in range(len(result_list)):
                wf.write(f"{size_decreases[i]:.3f},")
            for i in range(len(result_list)):
                wf.write(f"{performances[i]:.3f},")
            
            wf.write(f"{performance:.3f},{accepted}")

            for result in result_list:
                for res in result:
                    wf.write(f",{res[0]:.2f}")

            wf.write("\n")

    def get_base_performance(self, evaluations: int = 10):
        """ Get the performance of the "base" configuration. 
            This performance will be used to normalize all other results

        Args:
            evaluations (int, optional) Defaults to 10.
        """

        results_list = []
        writing_times = []
        processing_times = []

        for bench, data_file in zip(self.benchmark_files, self.data_files):

            results, writing_time, processing_time = self.configuration.evaluate(bench, data_file, evaluations, folder="generated_base", remove=False)

            results_list.append(results)
            writing_times.append(writing_time)
            processing_times.append(processing_time)

            mean_throughput, size, throughput_increase, size_decrease, performance = \
                get_performance(results, 0, 0, self.throughput_weight, is_base=True)

            self.base_throughputs.append(mean_throughput)
            self.base_sizes.append(size)

        throughput_increase = [0 for _ in bench]
        size_decrease = [0 for _ in bench]
        performances = [0 for _ in bench]

        self.current_performance = 0

        self.log_step(results_list, self.base_throughputs, throughput_increase, self.base_sizes, size_decrease, 
                      performances, self.current_performance, True, writing_times, processing_times)

    def evolve(self, steps: int = 100, evaluations: int = 10):
        """ Evolve the current configuration using the simmulated annealing algorithm

        Args:
            steps (int, optional): Number of steps to evolve for. Defaults to 100.
            evaluations (int, optional): Number of times to run a benchmark with a configuration. Defaults to 10.
        """
        self.write_file: str = f'results/annealer_multi_bench/{datetime.now().strftime("%y-%m-%d_%H:%M:%S")}.csv'
        
        with open(self.write_file, "w") as wf:
            for name in self.configuration.names:
                wf.write(f"{name},")

            for bench in self.benchmark_files:
                wf.write(f"throughput_{bench}(MB/s),")
            for bench in self.benchmark_files:
                wf.write(f"size_{bench}(MB),")
            for bench in self.benchmark_files:
                wf.write(f"writing_time_{bench}(s),")            
            for bench in self.benchmark_files:
                wf.write(f"processing_time_{bench}(s),")
            for bench in self.benchmark_files:
                wf.write(f"throughput_increase_{bench}(%),")
            for bench in self.benchmark_files:
                wf.write(f"size_decrease_{bench}(%),")
            for bench in self.benchmark_files:
                wf.write(f"performance_{bench}(%),")
                         
            wf.write(f"performance(%),accepted")

            for bench in self.benchmark_files:
                for i in range(evaluations):
                    wf.write(f",res_{bench}_{i}")

            wf.write("\n")

        # Log initial configuration
        print(f"Calculating Initial Performance")
        self.get_base_performance(evaluations)
        
        # evolve the configuration for the given number of steps
        print(f"Starting evolution")
        for i in range(steps):
            print(f"Step: {i} => Throughput: {self.current_performance:.3f}")
            self.step(i, evaluations)
