# Goals

The overall goal of this work is to explore the effect of the IO parameters.
This goal can be explored by answering the following questions:

1. How can we determine performance?
2. How can we improve performance?
3. Can we find an optimal set of parameters?
4. Is the optimal set of parameters the same for all problems?

# Parameters

A set of four parameters are used in this work: compression, page size, cluster size, and cluster bunch. All parameters aside from compression are discrete parameter, which means they can only have predefined values. Compression is a categorical parameter. This also means that it can only have predefined values, but there is no structure between the different values.   

# Mutating a configuration

Mutating a configuration is relatively simple. First, a parameter from the configuration is chosen. The value of this parameter is then changed. The way the value is changed is dependent on the type of parameter it is. The value of a discrete parameter can only be changed to one of its neighboring values, while the value of a categorical parameter can change to all other possible values. 

In some experiments, multiple parameters are changed when a configuration is mutated. In this case, a probability is given for the number of changes that should be made. Based on this probability, the number of parameters that should be changed is determined. That number of parameters are changed in the same way as described above. 

# Determening performance

The performance of a parameter configuration is determined using the four benchmarks: atlas, cms, h1, and lhcb. All benchmarks consist of two steps: First, a file is generated based on the page size, cluster size, and compression parameters. Second, the benchmark is executed on the new file. 

