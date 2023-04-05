import numpy as np
import os

###############################################################################################################################
###### Helper Functions
###############################################################################################################################


def get_runtime(outp: str, target: str = "Runtime-Main:") -> int:
    """Get the runtime of a benchmark based on the output

    Args:
        outp (str): benchmark output
        target (str, optional): what to read out. Defaults to "Runtime-Main:".

    Returns:
        int: the runtime
    """
    for line in outp.split("\n"):
        if target in line:
            return int(line.split(target)[1].strip()[:-2])


def get_metric(outp: str, target: str) -> float:
    """Get a metric from an benchmark output string

    Args:
        outp (str)
        target (str)

    Returns:
        float: value of the given metric
    """
    for line in outp.split("\n"):
        if target in line:

            return float(line.split("|")[-1].strip())
        
def get_throughput(outp: str) -> float:
    """ Calculate the throughput of a benchmark given its output
        Throughput is defined in MB/s based on the unzipped size, and total processing time
    
    Args:
        outp (str)

    Returns:
        float
    """
    volume = get_metric(outp, "RNTupleReader.RPageSourceFile.szUnzip")
    volume_MB = volume / 1_000_000

    upzip_time = get_metric(outp, "RNTupleReader.RPageSourceFile.timeWallUnzip")
    read_time = get_metric(outp, "RNTupleReader.RPageSourceFile.timeWallRead")
    total_time = upzip_time + read_time

    total_time_s = total_time / 1_000_000_000

    return volume_MB / total_time_s

def get_size(file_name: str) -> float:
    """Get the size of a benchmark file based on the output

    Args:
        outp (str)

    Returns:
        float
    """
    return os.stat(file_name).st_size

# def get_size(outp: str) -> float:
#     """Get the size of a benchmark file based on the output

#     Args:
#         outp (str)

#     Returns:
#         float
#     """
#     return get_metric(outp, "RNTupleReader.RPageSourceFile.bwReadUnzip")


def convertToByte(value: int, form: str = "b") -> int:
    """Convert value to byte, kilobyte, or megabyte

    Args:
        value (int)
        form (str, optional): The desired output. Defaults to "b".

    Returns:
        int
    """
    if form == "b" or form == "B":
        return value

    if form == "kb" or form == "KB":
        return value * 1024
    
    if form == "mb" or form == "MB":
        return value * 1_048_576
    
def convertToByteList(inp_list: list[tuple[int, str]]) -> list[int]:
    """ Convert a list of values using the convertToByte function 

    Args:
        inp_list (list[tuple[int, str]]): list of value, form pairs

    Returns:
        list[int]
    """
    return [convertToByte(x, y) for x,y in inp_list]

def convertByteToStr(inp_list: list[tuple[int, str]]) -> list[str]:
    """ Convert a list of values into a list of strings by concatinating them
    Args:
        inp_list (list[tuple[int, str]]): list of value, form pairs

    Returns:
        list[str]
    """
    return [str(f"{x} {y}") for x,y in inp_list]

def get_performance(results: list[tuple[int, int]], base_throughput: float, 
                    base_size: int, throughput_weight: float, is_base: bool=False) -> tuple[float, int, float, float, float]:
    
    """ Calculate the performance of a benchmark

    Args:
        results (list[tuple[int, int]]): The throughput and size of multiple runs
        base_throughput (float): The throughput of the base configuration
        base_size (int): The size of the base configuration
        throughput_weight (float): The ration between throughput and size for the performance calculation
        is_base (bool, optional): If true, the results are seen as the base results. Defaults to False.

    Returns:
        tuple[float, int, float, float, float]: mean_throughput, size, throughput_increase, size_decrease, performance
    """
    
    mean_throughput = np.mean([x[0] for x in results])
    size = results[0][1]

    if is_base:
        return mean_throughput, size, 0, 0, 0
    

    throughput_increase = ((mean_throughput - base_throughput) / base_throughput) * 100
    size_decrease = ((base_size - size) / base_size) * 100

    performance = throughput_weight * throughput_increase + \
                    (1-throughput_weight) * size_decrease
    
    return mean_throughput, size, throughput_increase, size_decrease, performance
