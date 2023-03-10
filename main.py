# %% 

import os 

# root [12] auto ntuple = ROOT::Experimental::RNTupleReader::Open("DecayTree" , "generated/B2HHH~none.ntuple")
# root [13] ntuple->PrintInfo(ROOT::Experimental::ENTupleInfo::kStorageDetails)

from dataclasses import dataclass
from random import randint, choice

import subprocess
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
###############################################################################################################################
###### Helper Functions
###############################################################################################################################


def get_runtime(outp: str, target: str = "Runtime-Main:"):
    for line in outp.split("\n"):
        if target in line:
            return int(line.split(target)[1].strip()[:-2])
        

def get_throughput(outp: str, target = "RNTupleReader.RPageSourceFile.bwRead"):
    for line in outp.split("\n"):
        if target in line:

            return float(line.split("|")[-1].strip())

def convertToByte(value: int, form: str = "b") -> int:
    if form == "b" or form == "B":
        return value

    if form == "kb" or form == "KB":
        return value * 1024
    
    if form == "mb" or form == "MB":
        return value * 1_048_576
    
def convertToByteList(inp_list: list[tuple[int, str]]) -> list[int]:
    return [convertToByte(x, y) for x,y in inp_list]

def convertByteToStr(inp_list: list[tuple[int, str]]) -> list[str]:
    return [str(f"{x} {y}") for x,y in inp_list]

###############################################################################################################################
###### Variables
###############################################################################################################################


@dataclass
class Variable:
    values: list
    value_names: list[str] = None
    variable_name: str = "no-variable_name"
    current_idx: int = None

    def __post_init__(self):
        if self.value_names == None:
            self.value_names = [str(x) for x in self.values]

        if self.current_idx == None:
            self.initialize()

    def initialize(self):
        self.current_idx = randint(0, len(self.values)-1)

    def step(self):
        raise NotImplementedError
    
    @property
    def value(self):
        return self.values[self.current_idx]
    
    def __str__(self) -> str:
        if self.current_idx == None:
            return f"Valiable {self.variable_name} is not yet initialized" 
        
        return f"{self.variable_name} \t=> {self.value_names[self.current_idx]}"

@dataclass
class DiscreteVariable(Variable):
    def step(self):
        if self.current_idx == 0:
            self.current_idx = 1
            return
        
        if self.current_idx == len(self.values)-1:
            self.current_idx = len(self.values)-2
            return

        self.current_idx = choice([self.current_idx - 1, 
                                   self.current_idx + 1])

        print(self.current_idx)

@dataclass
class CategoricalVariable(Variable):
    def step(self):
        self.current_idx = choice([x for x in range(len(self.values)) if x != self.current_idx])

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

    def __post_init__(self):
        if self.compression_var == None:
            self.createBaseConfig()

        self.variables = [self.compression_var, 
                          self.page_size_var,
                          self.cluster_size_var,
                          self.cluster_bunch_var]

    def createBaseConfig(self):
        self.compression_var = CategoricalVariable(["none", "zlib", "lz4", "lzma", "zstd"], 
                                                variable_name="compression", current_idx=2)
        
        page_sizes = [(16,"KB"), (32,"KB"), (64,"KB"), (128,"KB"), (256,"KB"), (512,"KB"),
            (1,"MB"), (2,"MB"), (4,"MB"), (8,"MB"), (16,"MB")]
        self.page_size_var = DiscreteVariable(convertToByteList(page_sizes), 
                                        value_names=convertByteToStr(page_sizes),
                                        variable_name="Page Size", current_idx=2)

        cluster_sizes = [(20,"MB"), (30,"MB"), (40,"MB"), (50,"MB"), (100,"MB"), (200,"MB"),
                        (300,"MB"), (400,"MB"), (500,"MB")]
        self.cluster_size_var = DiscreteVariable(convertToByteList(cluster_sizes), 
                                        value_names=convertByteToStr(cluster_sizes),
                                        variable_name="Cluster Size", current_idx=3)
        
        self.cluster_bunch_var = DiscreteVariable([1,2,3,4,5], variable_name="Cluster Bunch", current_idx=0)

    def randomize(self):
        for var in self.variables:
            var.initialize()

    def step(self):
        self.previous_variables = [x for x in self.variables]
        self.variables[choice([0, len(self.variables)-1])].step()

    def revert(self):
        self.variables = self.previous_variables


    def __str__(self) -> str:
        s = f"Current configuration:\n"

        for var in self.variables:
            s += f"{var.__str__()}\n"

        return s

# %%

@dataclass
class Climber:
    configuration: Configuration = None
    benchmark: str = "lhcb"
    file_name: str = "B2HHH"

    def __post_init__(self):
        if self.configuration == None:
            self.configuration = Configuration()

    def generate_file(self, conf: Configuration):
        compression = conf.compression_var.value
        page_size = conf.page_size_var.value
        cluster_size = conf.cluster_size_var.value

        executable_gen = f"iotools-master/gen_{self.benchmark}"
        input_file = "ref/B2HHH~zstd.root"
        output_folder = "generated"
        output_file = f"{output_folder}/{self.file_name}~{compression}_{page_size}_{cluster_size}.ntuple"

        if os.path.exists(output_file):
            return


        out = subprocess.getstatusoutput(f"./{executable_gen} -i {input_file} -o {output_folder} -c {compression} -p {page_size} -x {cluster_size}")

    def run_benchmark(self, conf: Configuration):


        compression = conf.compression_var.value
        page_size = conf.page_size_var.value
        cluster_size = conf.cluster_size_var.value

        executable = f"iotools-master/{self.benchmark}"
        input_file = f"generated/{self.file_name}~{compression}_{page_size}_{cluster_size}.ntuple"
        use_rdf = "" # boolean: -r if true
        cluster_bunch = conf.cluster_bunch_var.value

        os.system('sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"')
        out = subprocess.getstatusoutput(f"./{executable} -i {input_file} -x {cluster_bunch} {use_rdf} -p")

        return get_throughput(out[1])

    def evaluate_configuration(self, conf:Configuration):

        self.generate_file(conf)
        
        results = []
        for _ in tqdm(range(50)):
            results.append(self.run_benchmark(conf))

        results = np.array(results)
        print(f"{results.mean() = }\n{results = }")

        with open("results/test.csv", "a") as wf:
            for result in results:
                wf.write(f"{result}\n")

    


# %%

conf = Configuration()
climber = Climber(conf)
climber.evaluate_configuration(conf)

# %%
