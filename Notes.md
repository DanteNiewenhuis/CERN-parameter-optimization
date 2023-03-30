## Week 1

- Had first meeting where the general plans were laid out. 
- In total we are going to use four benchmarks (start with only LHCb)
    - LHCb
    - CMS
    - Atlas
    - H1

- We start with the following parameters to use:
    - Compression Algorithm
    - Page Size
    - Cluster Size
    - Cluster Bunch

- Aside from these, more parameters are available:
    - RDF or not
    - Multithreading
    - SSD vs HDD
    - Compression can be split into level and type

- Started with making the benchmarks run
- Created basic HillClimber

## Week 2

- Created classes for all parameters
- Finished the basic HillClimber
- Connected HillClimber to executing the benchmarks

- Throughput metric from the benchmark is incorrect 
    - Throughput is now calculated by hand 

- The HillClimber seem to get stuck in local maxima
    - Instead a Simulated annealer is used

- Aside from the Throughput, the size is now added as a penalty
- The performance is now the relative throughput - relative size.

- throughput and size are relative to the base parameters of ROOT.

- First (temp = 0.1, falloff = 0.9) run was successful, but the temperature  seems to be too high. 
- Second run, the temperature is lowereed to 0.05. (still seems too high)

### 29 - 3
- Rewrote code
    - Now every thing is structered in the PythonFiles folder
    - Moved functions around so they are more logically placed

- Tried running lhcb

### 30 - 3
- lhcb run was not completely successful. 
    - High performance was reached, but many bad results were accepted

- Found out the temperature schedule was not working correctly
- Changed temperature schedule.
- Using a temperature const of 1 is too low, and results in too little results being accepted (A local minima is reached very fast). 

- Adding possibility of changing multiple parameters