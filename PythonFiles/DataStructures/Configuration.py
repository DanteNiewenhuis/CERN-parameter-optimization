from dataclasses import dataclass
from random import choice

from PythonFiles.utils import convertToByteList, convertByteToStr, get_throughput, get_size, get_memory
from PythonFiles.DataStructures.Variable import Variable, CategoricalVariable, DiscreteVariable, \
                                                getCompressionVar, getClusterSizeVar, getClusterBunchVar, getPageSizeVar

import os
import subprocess
from tqdm import tqdm
import time

import numpy as np

###############################################################################################################################
###### Variables
###############################################################################################################################


###############################################################################################################################
###### Configuration
###############################################################################################################################

@dataclass
class Configuration:
    compression_var: CategoricalVariable = None
    page_size_var: DiscreteVariable = None
    cluster_size_var: DiscreteVariable = None
    cluster_bunch_var: DiscreteVariable = None

    variables: list[Variable] = None
    mutated_variable: Variable = None

    mutated_variables: list[Variable] = None

    def __post_init__(self):
        if self.compression_var == None:
            self.createBaseConfig()

        self.variables = [self.compression_var, 
                          self.page_size_var,
                          self.cluster_size_var,
                          self.cluster_bunch_var]
        
    @property
    def names(self) -> list[str]:
        return [var.variable_name for var in self.variables]
    
    @property
    def values(self) -> list[str]:
        return [var.value for var in self.variables]
            

    def createBaseConfig(self):
        """ Creates the configuration that is the default configuration defined by ROOT
        """
        self.compression_var = CategoricalVariable("compression", ["none", "zlib", "lz4", "lzma", "zstd"], current_idx=2)
        
        page_sizes = [(16,"KB"), (32,"KB"), (64,"KB"), (128,"KB"), (256,"KB"), (512,"KB"),
            (1,"MB"), (2,"MB"), (4,"MB"), (8,"MB"), (16,"MB")]
        self.page_size_var = DiscreteVariable("Page Size", convertToByteList(page_sizes), 
                                        value_names=convertByteToStr(page_sizes), current_idx=2)

        cluster_sizes = [(20,"MB"), (30,"MB"), (40,"MB"), (50,"MB"), (100,"MB"), (200,"MB"),
                        (300,"MB"), (400,"MB"), (500,"MB")]
        self.cluster_size_var = DiscreteVariable("Cluster Size", convertToByteList(cluster_sizes), 
                                        value_names=convertByteToStr(cluster_sizes), current_idx=3)
        
        self.cluster_bunch_var = DiscreteVariable("Cluster Bunch", [1,2,3,4,5], current_idx=0)

    def randomize(self):
        """ Change all variables to a random value
        """
        for var in self.variables:
            var.initialize()

    def step(self):
        """ Make a random variable set a step
        """
        self.mutated_variable = self.variables[choice(range(len(self.variables)))]
        self.mutated_variable.step()

    def step_multi(self, prop):
        x = np.arange(len(self.variables)) + 1
        number_of_changes = np.random.choice(x, p=prop)

        idxs_to_change = np.random.choice(x-1, number_of_changes, replace=False)

        self.mutated_variables = []
        for i in idxs_to_change:
            self.variables[i].step()
            self.mutated_variables.append(self.variables[i])

        return number_of_changes

    def revert(self):
        """ Revert the previous step
        """
        self.mutated_variable.revert()

    def revert_multi(self):
        for var in self.mutated_variables:
            var.revert()
        
        self.mutated_variables = []

    def __str__(self) -> str:
        s = f"Current configuration:\n"

        for var in self.variables:
            s += f"{var.__str__()}\n"

        return s
    
    def generate_file(self, benchmark_file: str, data_file: str, output_folder:str = "generated") -> str:
        """ Genereate a benchmark file based on the current configuration

        Args:
            benchmark_file (str): The type of benchmark to generate
            data_file (str): The data file that should be used for generation

        Returns:
            str: full name of the generated file
        """
        compression = self.compression_var.value
        page_size = self.page_size_var.value
        cluster_size = self.cluster_size_var.value

        executable_gen = f"../iotools/gen_{benchmark_file}"
        input_file = f"ref/{data_file}~zstd.root"
        output_file = f"{output_folder}/{data_file}~{compression}_{page_size}_{cluster_size}.ntuple"

        if os.path.exists(output_file):
            print(f"output file already available => {output_file = }")
            return output_file

        print(f"Generating file => {output_file}")

        print(f"./{executable_gen} -i {input_file} -o {output_folder} -c {compression} -p {page_size} -x {cluster_size}")

        os.system(f"./{executable_gen} -i {input_file} -o {output_folder} -c {compression} -p {page_size} -x {cluster_size}")

        return output_file

    def run_benchmark(self, benchmark: str, data_file: str, input_folder: str = "generated") -> float:
        """ Run a benchmark based on the current configuration

        Args:
            benchmark_file (str): The type of benchmark to generate
            data_file (str): The data file that is used for generation

        Returns:
            float: the throughput of the benchmark
        """
        compression = self.compression_var.value
        page_size = self.page_size_var.value
        cluster_size = self.cluster_size_var.value

        executable = f"../iotools/{benchmark}"
        input_file = f"{input_folder}/{data_file}~{compression}_{page_size}_{cluster_size}.ntuple"
        use_rdf = "" # boolean: -r if true
        cluster_bunch = self.cluster_bunch_var.value

        os.system('sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"')
        out = subprocess.getstatusoutput(f"/usr/bin/time  ./{executable} -i {input_file} -x {cluster_bunch} {use_rdf} -p")



        return get_throughput(out[1]), get_memory(out[1])
    
    def evaluate(self, benchmark_file: str, data_file: str, evaluations: int = 10, folder:str = "generated", remove: bool = True) -> list[float]:
        """ Evaluate the current configuration using a specific benchmark. 
            The benchmark is generated, and run multiple times.

        Args:
            benchmark_file (str): The type of benchmark to generate
            data_file (str): The data file that is used for generation
            evaluations (int, optional): number of times the benchmark should be run. Defaults to 10.

        Returns:
            list[float]: The throughput of each run
        """
        
        print(f"Evaluating configuration:\n {str(self)}")


        start = time.time()
        output_file = self.generate_file(benchmark_file, data_file, folder)
        end = time.time()
        writing_time = end - start


        size = get_size(output_file)
        results = []
        start = time.time()
        for _ in tqdm(range(evaluations)):
            throughput, memory = self.run_benchmark(benchmark_file, data_file, folder)
            results.append((throughput, size, memory))
        end = time.time()
        processing_time = end - start
        
        if remove:
            os.remove(output_file)

        return results, writing_time, processing_time


def getConfiguration(compression, page_size, cluster_size, cluster_bunch):
    compression_var = getCompressionVar(compression)
    page_size_var = getPageSizeVar(int(page_size))
    cluster_size_var = getClusterSizeVar(int(cluster_size))
    cluster_bunch_var = getClusterBunchVar(int(cluster_bunch))

    return Configuration(compression_var=compression_var,
                         page_size_var=page_size_var,
                         cluster_size_var=cluster_size_var,
                         cluster_bunch_var=cluster_bunch_var)
