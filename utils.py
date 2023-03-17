import os
import subprocess

###############################################################################################################################
###### Helper Functions
###############################################################################################################################


def get_runtime(outp: str, target: str = "Runtime-Main:") -> int:
    for line in outp.split("\n"):
        if target in line:
            return int(line.split(target)[1].strip()[:-2])


def get_metric(outp: str, target = "RNTupleReader.RPageSourceFile.bwReadUnzip"):   
    for line in outp.split("\n"):
        if target in line:

            return float(line.split("|")[-1].strip())
        
def get_throughput(outp: str) -> float:
    volume = get_metric(outp, "RNTupleReader.RPageSourceFile.szUnzip")
    volume_MB = volume / 1_000_000

    upzip_time = get_metric(outp, "RNTupleReader.RPageSourceFile.timeWallUnzip")
    read_time = get_metric(outp, "RNTupleReader.RPageSourceFile.timeWallRead")
    total_time = upzip_time + read_time

    total_time_s = total_time / 1_000_000_000

    return volume_MB / total_time_s

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

def generate_file(conf, benchmark: str, data_file: str):    
    compression = conf.compression_var.value
    page_size = conf.page_size_var.value
    cluster_size = conf.cluster_size_var.value

    executable_gen = f"iotools-master/gen_{benchmark}"
    input_file = f"ref/{data_file}~zstd.root"
    output_folder = "generated"
    output_file = f"{output_folder}/{data_file}~{compression}_{page_size}_{cluster_size}.ntuple"

    if os.path.exists(output_file):
        return output_file

    print(f"Generate file => {output_file}")

    print(f"./{executable_gen} -i {input_file} -o {output_folder} -c {compression} -p {page_size} -x {cluster_size}")

    os.system(f"./{executable_gen} -i {input_file} -o {output_folder} -c {compression} -p {page_size} -x {cluster_size}")

    return output_file

def run_benchmark(conf, benchmark: str, data_file: str) -> float:
    compression = conf.compression_var.value
    page_size = conf.page_size_var.value
    cluster_size = conf.cluster_size_var.value

    executable = f"iotools-master/{benchmark}"
    input_file = f"generated/{data_file}~{compression}_{page_size}_{cluster_size}.ntuple"
    use_rdf = "" # boolean: -r if true
    cluster_bunch = conf.cluster_bunch_var.value

    os.system('sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"')
    out = subprocess.getstatusoutput(f"./{executable} -i {input_file} -x {cluster_bunch} {use_rdf} -p")

    return get_throughput(out[1]), out