from dataclasses import dataclass
from random import randint, choice

from utils import convertToByteList, convertByteToStr

###############################################################################################################################
###### Variables
###############################################################################################################################


@dataclass
class Variable:
    values: list
    value_names: list[str] = None
    variable_name: str = "no-variable_name"
    current_idx: int = None
    previous_idx: int = None

    def __post_init__(self):
        if self.value_names == None:
            self.value_names = [str(x) for x in self.values]

        if self.current_idx == None:
            self.initialize()

    def initialize(self):
        self.current_idx = randint(0, len(self.values)-1)

    def step(self):
        raise NotImplementedError

    def revert(self):
        self.current_idx = self.previous_idx
    
    @property
    def value(self) -> list:
        return self.values[self.current_idx]
    
    def __str__(self) -> str:
        if self.current_idx == None:
            return f"Valiable {self.variable_name} is not yet initialized" 
        
        return f"{self.variable_name} \t=> {self.value_names[self.current_idx]}"

@dataclass
class DiscreteVariable(Variable):
    def step(self):
        self.previous_idx = self.current_idx
        if self.current_idx == 0:
            self.current_idx = 1
            return
        
        if self.current_idx == len(self.values)-1:
            self.current_idx = len(self.values)-2
            return

        self.current_idx = choice([self.current_idx - 1, 
                                   self.current_idx + 1])

@dataclass
class CategoricalVariable(Variable):
    def step(self):
        self.previous_idx = self.current_idx
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
    mutated_variable: Variable = None

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
        self.mutated_variable = self.variables[choice(range(len(self.variables)))]
        self.mutated_variable.step()

    def revert(self):
        self.mutated_variable.revert()

    def __str__(self) -> str:
        s = f"Current configuration:\n"

        for var in self.variables:
            s += f"{var.__str__()}\n"

        return s