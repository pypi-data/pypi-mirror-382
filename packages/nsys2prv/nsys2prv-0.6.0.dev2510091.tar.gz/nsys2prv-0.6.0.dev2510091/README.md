<center>
<img src="docs/h-color.png" alt="logo" width="40%">

# nsys2prv: Translate NVIDIA Nsight Systems traces to Paraver traces

![PyPI - Version](https://img.shields.io/pypi/v/nsys2prv)
![Gitlab Pipeline Status](https://gitlab.pm.bsc.es/beppp/nsys2prv/badges/main/pipeline.svg
)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nsys2prv)
</center>

_nsys2prv_ is a Python package that parses and interprets the exported data of an NVIDIA Nsight Systems[^1] report and converts it to Paraver semantics in order to browse the trace with Paraver.  Paraver is a parallel performance analysis tool by the Performance Tools team at BSC, and is a parallel trace visualization system allowing for large scale trace execution analysis. Paraver can be obtained at [https://tools.bsc.es/downloads](https://tools.bsc.es/downloads).

The Nsight Systems traces should include minimum GPU kernel activity. Apart from this, _nsys2prv_ can also translate information about CUDA runtime, OpenACC constructs, MPI runtime, GPU metrics and NVTX regions. In addition to the different programming model semantics, one of the main features of _nsys2prv_ is its ability to **merge different Nsight Systems reports into one trace, allowing for easier analysis of multi-node, large scale parallel executions.**

## How it works
This tool relies on the export functionality of `nsys`. The data collection consists of a mix of the `nsys stats` predefined scripts, and a manual parsing of the _.sqlite_ exported format data.  The following figure summarizes the translation workflow:
![translation workflow](docs/translate-workflow.png)

More details on the workflow and the data parsing logic can be read on the [wiki pages](https://pm.bsc.es/gitlab/beppp/nsys2prv/-/wikis/Home).

## Installation

_nsys2prv_ is distributed as a PyPI package and thus can be installed with `pip`. The following requirements for the package to work will be installed automatically by `pip`:
- python >= 3.10
- pandas > 2.2.2
- sqlalchemy
- tqdm

Additionally, it requires an installation of NIDIA Nsight Systems in your _PATH_ to extract the data. Alternatively, you can set the NSYS_HOME environment variable.  It is required that the version of Nsight Systems is always greater than the one used to obtain the trace. **For translating, a minumum version of 24.6 is required**.

To install the package just use `pip` globally or create a vitual environment:
```bash
pip install --global nsys2prv
# or
python -m venv ./venv
source ./venv/bin/activate
pip install nsys2prv
```

## Basic usage
To translate a trace from Nsight Systems you need the _.nsys-rep_ report file that `nsys profile` outputs.  The basic usage of _Nsight Systems_ to get a trace is the following:

```bash
nsys profile --gpu-metrics-devices=cuda-visible -t cuda,nvtx -o ./llm_all --capture-range=nvtx --env-var=NSYS_NVTX_PROFILER_REGISTER_ONLY=0 --nvtx-capture=RANGE_NAME python TestLLAMA.py
```

In this example, we ask the profiler to only trace during the “RANGE_NAME” NVTX range, to get a trace for our phase of interest.

This should output the _llm\_all.nsys-rep_ file, that serves as input to `nsys2prv`.
```bash
nsys2prv -t type1,type2 llm_all.nsys-rep output-paraver-name
```

Currently, the translator needs that the user manually specifies the different programming models information to translate using the `--trace,-t` flag. By default it always extracts kernel execution information, so it is mandatory that the nsys report contains GPU activity. Future releases will automatically detect the information that is available in the report and make this flag optional.  The accepted value for the flag is a comma-separated list with any of the following categories:  
- `cuda_api_trace`: CUDA API calls
- `nvtx_pushpop_trace`: The developer defined NVTX Push/Pop regions
- `nvtx_startend_trace`: The developer defined NVTX Start/End regions
- `gpu_metrics`: The sampling events of hardware metrics for the GPUs
- `mpi_event_trace`: The MPI calls
- `openacc`: The OpenACC constructs
- `graphs`: If your trace includes CUDA Graphs, include this flag to make sure that all Graph activity is translated, wether it is Node tracing or Graph tracing. If you are not sure, you can still include it and it will be disabled if there are no CUDA Graphs.
- `nccl`: If your application has NCCL activity, you can add this flag to include the NCCL payloads (e.g. communication size, reduction operation, root rank, etc.) in the NCCL kernel events.

Finally, the `output-paraver-name.prv` trace can be opened with Paraver and analyzed.

For multi-report translation, simply add the `-m` flag and add all the _.nsys-rep_ files:
```bash
nsys2prv -t type1,type2 -m source_rank0.nsys-rep [source_rank1.nsys-rep [source_rank2.nsys-rep ...]] output-paraver-name

```

## How to analyze your trace
A predefined set of Paraver Config Files (CFGs) can be found in the `cfgs` directory of this repository. If you open these files with Paraver, you will see predefined windows showing the information available in the trace. Some of them are more advanced and will show analysis views.

Config files are grouped in 4 different sets:

| Folder       | Description                                                                                                   |
|--------------|---------------------------------------------------------------------------------------------------------------|
| _basics_     | Configurations that show the available raw events in timelines                                                |
| _views_      | Compound views to show different behaviors and kernel semantics                                               |
| _analysis_   | More complex configurations aimed to summarize insight in the form of efficiency metrics from derived metrics |
| _hwcounters_ | Specific views to show hardware counters obtained with "gpu-metrics" flag                                     |

**As a starting point**, the _views/cuda\_activities.cfg_ configuration file will show a timeline aggregating all CUDA-related activities: CUDA API calls, kernel execution at the GPU and memory operations.

For documentation about trace analysis and config files (CFGs) provided, please refer to the [wiki pages](https://pm.bsc.es/gitlab/beppp/nsys2prv/-/wikis/Home).

## Bug reporting and contribution
A list of the current bugs and features targeted can be seen in the GitLab repository. The project is still currently under initial development and is expecting a major code refactoring and changes in the command line interface (CLI).  As it is a tool to support and enable performance analysts' work, new use cases or petitions for other programming model information support are always welcomed. Please contact marc.clasca@bsc.es or beppp@bsc.es for any of those requests, recommendations, or contribution ideas.

If you are a regular user and would like to receive updates on new important releases and bug fixes, you can subscribe to the users mailing list sending an email to nsys2prv-users-join@bsc.es.


[^1]: https://developer.nvidia.com/nsight-systems