# %% 

# root [12] auto ntuple = ROOT::Experimental::RNTupleReader::Open("DecayTree" , "generated/B2HHH~none.ntuple")
# root [13] ntuple->PrintInfo(ROOT::Experimental::ENTupleInfo::kStorageDetails)

from dataclasses import dataclass
from tqdm import tqdm
from datetime import datetime

from Configuration import Configuration
import numpy as np



# %%

@dataclass
class Climber:
    configuration: Configuration = None
    benchmark: str = "lhcb"
    file_name: str = "B2HHH"

    def __post_init__(self):
        if self.configuration == None:
            self.configuration = Configuration()

    def evaluate_configuration(self, conf:Configuration, evaluations: int = 10) -> list[float]:

        self.generate_file(conf)
        
        results = []
        for _ in tqdm(range(evaluations)):
            results.append(self.run_benchmark(conf))

        return results

    def step(self, evaluations: int = 10):
        self.configuration.step()
        
        results = self.evaluate_configuration(self.configuration, evaluations)
        _performance = np.mean(results)

        if _performance > self.performance:
            self.log_step(results, True)
            self.performance = _performance
        
        else:
            self.log_step(results, False)
            self.configuration.revert()
            

    def log_step(self, results, success:bool = False):
        with open(self.write_file, "a") as wf:
            for value in self.configuration.values:
                wf.write(f"{value},")

            wf.write(f"{np.mean(results):.2f},{np.std(results):.2f},{success}")

            for res in results:
                wf.write(f",{res:.1f}")

            wf.write("\n")

    def evolve(self, steps: int = 100, evaluations: int = 10):
        self.write_file: str = f'results/climber/{datetime.now().strftime("%y-%m-%d_%H:%M:%S")}.csv'
        
        with open(self.write_file, "w") as wf:
            for name in self.configuration.names:
                wf.write(f"{name},")

            wf.write(f"res_mean,res_std,success")

            for i in range(evaluations):
                wf.write(f",res_{i}")

            wf.write("\n")

        # Log initial configuration
        print(f"Calculating Initial Performance")
        results = self.evaluate_configuration(self.configuration, evaluations)
        self.performance = np.mean(results)
        self.log_step(results, True)
        
        # evolve the configuration for the given number of steps
        print(f"Starting evolution")
        for i in range(steps):
            print(f"Step: {i} => Throughput: {self.performance:.3f}")
            self.step(evaluations)