#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import argparse
import time
import subprocess
import os
import locale
import json
import numpy as np 
import csv  # Add import for CSV
from datetime import datetime  # Add import for timing
from functools import reduce
from sqlalchemy import create_engine, text, dialects
from sqlalchemy.exc import OperationalError
from .EventWriter import event_writer as ewr
from .NSYSInterface import NSYSInterface
from .semantics.mpi_event_encoding import *
from .semantics import *

def warn(message):
    print("\033[93m Warning: ", message, "\033[00m")

# Define the CSV file name for storing timings
TIMINGS_CSV_FILE = "timings.csv"

def write_timings_to_csv(timings, num_reports, total_events):
    """Write timing information to a CSV file."""
    file_exists = os.path.isfile(TIMINGS_CSV_FILE)
    with open(TIMINGS_CSV_FILE, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        now = datetime.now().isoformat()
        if not file_exists:
            # Write header if the file doesn't exist
            writer.writerow(["Timestamp", "Region", "Duration (s)", "Num Reports", "Total Events"])
        for region, duration in timings.items():
            writer.writerow([now, region, duration, num_reports, total_events])

def main():
    locale.setlocale(locale.LC_ALL, '')

    print("nsys2prv v0.6.0-dev2510091")

    class ShowVersion(argparse.Action):
        def __call__(self, parser, namespace, values, option_string):
            print("Version for paper camera-ready with timing instrumentation")
            print("export SQLite schema version compatibility version 3.17")
            parser.exit() # exits the program with no more arg parsing and checking


    parser = argparse.ArgumentParser(description="Translate a NVIDIA Nsight System trace to a Paraver trace",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    epilog="The nsys executable needs to be in the PATH, or the environment variable NSYS_HOME needs to be set.  If using postprocessing, the PARAVER_HOME variable needs to be set.")

    parser.add_argument("-v", "--version",  nargs=0, help="Show version and exit.", action=ShowVersion)
    parser.add_argument("-f", "--filter-nvtx", help="Filter by this NVTX range")
    parser.add_argument("-t", "--trace", help="Comma separated names of events to translate: [mpi_event_trace, nvtx_pushpop_trace, nvtx_startend_trace, cuda_api_trace, gpu_metrics, openacc, nccl, graphs]")
    parser.add_argument("-m", "--multi-report", action="store_true", help="Translate multiple reports of the same execution into one trace.")

    parser.add_argument("--force-sqlite", action="store_true", help="Force Nsight System to export SQLite database")

    parser.add_argument("-s", "--sort", action="store_true", help="Sort trace at the end")
    parser.add_argument("-z", "--compress", action="store_true", help="Compress trace at the end with gzip")
    parser.add_argument("--timing", action="store_true", help="Report translation time of different phases and write to a file")
    #parser.add_argument("-n", "--nvtx-stack-range", nargs=2, type=int)

    parser.add_argument("source_rep", nargs="+", help="Nsight source report file")
    parser.add_argument("output", help="Paraver output trace name")

    args = parser.parse_args()

    # Start timing the entire execution
    start_time = time.time()

    # Dictionary to store timings for coarse regions
    timings = {}

    # Timing: Trace configuration and setup
    region_start = time.time()
    # # Trace configuration and setup
    
    PARAVER_HOME = os.getenv('PARAVER_HOME')

    MULTIREPORT = args.multi_report
    if MULTIREPORT:
        REPORTS_LIST = [os.path.abspath(x) for x in args.source_rep]
        REPORT_DIRS_LIST = [os.path.dirname(x) for x in REPORTS_LIST]
        REPORT_FILE = REPORTS_LIST[0] # For fast checks, it's best to have a reference report
    else:
        REPORT_FILE = os.path.abspath(args.source_rep[0])
        REPORT_DIR = os.path.dirname(REPORT_FILE)
    
    trace_name = args.output

    NVTX_FILTER = args.filter_nvtx != None
    NVTX_RANGE = args.filter_nvtx

    reports = args.trace.split(",")

    reports_og = reports.copy()
    reports_og.append('cuda_gpu_trace') # Manually add the mandatory kernel info

    t_nvtx = False
    t_nvtx_startend = False
    t_apicalls = False
    t_mpi = False
    t_metrics = False
    t_openacc = False
    t_nccl = False
    t_graphs = False

    if "nvtx_pushpop_trace" in reports: 
        t_nvtx = True 
        reports.remove("nvtx_pushpop_trace")
    if "cuda_api_trace" in reports: t_apicalls = True
    if "mpi_event_trace" in reports: 
        t_mpi = True
        reports.remove("mpi_event_trace")
    if "gpu_metrics" in reports: 
        t_metrics = True
        reports.remove("gpu_metrics")
    if "nvtx_startend_trace" in reports: 
        t_nvtx_startend = True
        reports.remove("nvtx_startend_trace")
    if "openacc" in reports:
        t_openacc = True
        reports.remove("openacc")
    if "nccl" in reports:
        t_nccl = True
        reports.remove("nccl")
        if not t_nvtx:
            warn("NCCL information require NVTX regions to be present. Enabling NVTX traces.")
            t_nvtx = True
    if "graphs" in reports:
        t_graphs = True
        reports.remove("graphs")

    
    event_type_api = 63000000
    event_type_nvtx = 9003
    event_type_nvtx_startend = 9004
    
    event_type_mpi = 9300
    event_type_metrics_base = 9400

    event_type_nvtx_base = 9600
    event_type_nvtx_nesmik = 81000
    event_type_nvtx_nccl = 9500

    event_type_openacc = 66000000
    event_type_openacc_data = 66000001
    event_type_openacc_launch = 66000002

    event_type_name_openacc = 66100000
    event_type_name_openacc_data = 66100001
    event_type_name_openacc_launch = 66100002

    event_type_func_openacc = 66200000
    event_type_func_openacc_data = 66200001
    event_type_func_openacc_launch = 66200002

    event_type_openacc_data_size = 66300001

    comm_tag_launch = 55001
    comm_tag_memory = 55002
    comm_tag_dependency = 55003

    nvtx_select_frames = False
    nvtx_stack_top = 1
    nvtx_stack_bottom = 4

    nsi = NSYSInterface(reports, NVTX_FILTER, NVTX_RANGE, args.force_sqlite)

    if MULTIREPORT:
        print(f"Multiple reports provided: {REPORTS_LIST}")
    print("Extracting reports for: {}".format(reports_og))
    
    if MULTIREPORT:
        for REPORT_FILE_I in REPORTS_LIST:
            print(f"Exporting SQLite databse for {os.path.basename(REPORT_FILE_I)}")
            nsi.check_export_report(REPORT_FILE_I)
    else:
        nsi.check_export_report(REPORT_FILE)

    engine = create_engine(f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")
    metadata = pd.read_sql_table("META_DATA_EXPORT", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")
    minor_version = metadata.loc[metadata["name"] == "EXPORT_SCHEMA_VERSION_MINOR"]
    micro_version = metadata.loc[metadata["name"] == "EXPORT_SCHEMA_VERSION_MICRO"]
    if int(minor_version["value"].iloc[0]) > 17 or int(minor_version["value"].iloc[0]) < 11:
        print(f"\033[93m Warning! The SQLite schema version {int(minor_version['value'].iloc[0])} is greater or lower than the tested ones (11 < v =< 17). If unexpected behaviour occurs, please report it. \033[00m")

    # Check compatibility with deviceId matching feature
    deviceId_matching_compat = ((int(minor_version['value'].iloc[0]) == 16) and (int(micro_version['value'].iloc[0]) >= 4)) or (int(minor_version['value'].iloc[0]) >= 17)


    if MULTIREPORT:
        for REPORT_FILE_I in REPORTS_LIST:
            print(f"Processing stats for {os.path.basename(REPORT_FILE_I)}")
            nsi.call_stats(REPORT_FILE_I)
    else:
        nsi.call_stats(REPORT_FILE)

    timings["Trace Configuration and Setup"] = time.time() - region_start

    # Timing: Import datasets
    region_start = time.time()
    # MARK: IMPORT DATASETS
    print("Importing datasets...")

    kernels_df = []
    if MULTIREPORT:
        for REPORT_FILE_I in REPORTS_LIST:
            ksi = KernelsSemantic(REPORT_FILE_I)
            ksi.Setup()
            ksi.load_data()
            kernels_df.append(ksi.get_df())
            del ksi
    else:
        ks = KernelsSemantic(REPORT_FILE)
        ks.Setup()
        ks.load_data()
        kernels_df = ks.get_df()


    if t_graphs:
        graphs_df = []
        graphs_mode = set()
        if MULTIREPORT:
            t_graphs = False # We need this to check if at least one of the reports contains graphs, because if not, disable graph processing
            for REPORT_FILE_I in REPORTS_LIST:
                cgi = CUDAGraphsSemantic(REPORT_FILE_I)
                t_graphs = cgi.Setup() or t_graphs # here we do the OR operation
                graphs_mode.add(cgi.tracing_mode)
                cgi.load_data()
                graphs_df.append(cgi.get_df())
                del cgi
            graphs_mode.discard("")
            graphs_mode = graphs_mode.pop()
        else:
            cg = CUDAGraphsSemantic(REPORT_FILE)
            t_graphs = cg.Setup()
            graphs_mode = cg.tracing_mode
            cg.load_data()
            graphs_df = cg.get_df()
            del cg
        print(f"\033[96m The tracing mode for CUDA Graphs was set to {graphs_mode}. \033[00m")

    if t_apicalls:
        cuda_api_df = []
        if MULTIREPORT:
            for i, REPORT_FILE_I in enumerate(REPORTS_LIST):
                cuda_api_df.append(pd.read_csv(nsi.build_nsys_stats_name(REPORT_FILE_I, REPORT_DIRS_LIST[i], "cuda_api_trace")))
        else:
            cuda_api_df = pd.read_csv(nsi.build_nsys_stats_name(REPORT_FILE, REPORT_DIR, "cuda_api_trace"))
    else:
        cuda_api_df = pd.DataFrame()

    if t_nvtx:
        nvtx_df = []
        if MULTIREPORT:
            for REPORT_FILE_I in REPORTS_LIST:
                kpi = NVTXPushPopSimpleSemantic(REPORT_FILE_I)
                kpi.Setup()
                kpi.load_data()
                nvtx_df.append(kpi.get_df())
                del kpi
        else:
            kp = NVTXPushPopSimpleSemantic(REPORT_FILE)
            kp.Setup()
            kp.load_data()
            nvtx_df = kp.get_df()
            del kp

    else:
        nvtx_df = pd.DataFrame()

    if t_nvtx_startend:
        nvtx_startend_df = []
        if MULTIREPORT:
            for REPORT_FILE_I in REPORTS_LIST:
                ksi = NVTXStartEndSemantic(REPORT_FILE_I)
                ksi.Setup()
                ksi.load_data()
                nvtx_startend_df.append(ksi.get_df())
                del ksi
        else:
            ks = NVTXStartEndSemantic(REPORT_FILE)
            ks.Setup()
            ks.load_data()
            nvtx_startend_df = ks.get_df()
            del ks
    else:
        nvtx_startend_df = pd.DataFrame()

    if t_mpi:
        mpi_df = []
        try:
            if MULTIREPORT:
                for REPORT_FILE_I in REPORTS_LIST:
                    kp2pi = MPIP2PSemantic(REPORT_FILE_I)
                    kp2pi.Setup()
                    kp2pi.load_data()
                    kp2pi.postprocess()

                    kcolli = MPICollSemantic(REPORT_FILE_I)
                    kcolli.Setup()
                    kcolli.load_data()

                    kotheri = MPIOtherSemantic(REPORT_FILE_I)
                    kotheri.Setup()
                    kotheri.load_data()

                    krmai = MPIRMASemantic(REPORT_FILE_I)
                    krmai.Setup()
                    krmai.load_data()

                    kioi = MPIIOPSemantic(REPORT_FILE_I)
                    kioi.Setup()
                    kioi.load_data()

                    mpi_df.append(pd.concat([kp2pi.get_df(), kcolli.get_df(), kotheri.get_df(), krmai.get_df(), kioi.get_df()], ignore_index=True))
                del kp2pi, kcolli, kotheri, krmai, kioi
                if all(df.empty for df in mpi_df): t_mpi = False
            else:
                kmpi = MPIP2PSemantic(REPORT_FILE)
                kmpi.Setup()
                kmpi.load_data()
                kmpi.postprocess()
                mpi_p2p_df = kmpi.get_df()

                kmpi = MPICollSemantic(REPORT_FILE)
                kmpi.Setup()
                kmpi.load_data()
                mpi_coll_df = kmpi.get_df()

                kmpi = MPIOtherSemantic(REPORT_FILE)
                kmpi.Setup()
                kmpi.load_data()
                mpi_other_df = kmpi.get_df()

                kmpi = MPIRMASemantic(REPORT_FILE)
                kmpi.Setup()
                kmpi.load_data()
                mpi_rma_df = kmpi.get_df()

                kmpi = MPIIOPSemantic(REPORT_FILE)
                kmpi.Setup()
                kmpi.load_data()
                mpi_io_df = kmpi.get_df()
                mpi_df = pd.concat([mpi_p2p_df, mpi_coll_df, mpi_other_df, mpi_rma_df, mpi_io_df], ignore_index=True)
                del kmpi, mpi_p2p_df, mpi_coll_df, mpi_other_df, mpi_rma_df, mpi_io_df
                if mpi_df.empty: t_mpi = False
        except OperationalError as oe:
            print("There has been a problem fetching MPI information. MPI data will be skipped.")
            print(f"[ERROR]: {oe.args[0]}")
            t_mpi = False
    else:
        mpi_df = pd.DataFrame()

    gpu_metrics_agg = []
    metrics_event_names = []
    if t_metrics:
        if MULTIREPORT:
            t_metrics = False
            for REPORT_FILE_I in REPORTS_LIST:
                ksi = GPUMetricsSemantic(REPORT_FILE_I)
                t_metrics = ksi.Setup() or t_metrics
                ksi.load_data()
                gpu_metrics_agg.append(ksi.get_df())
                metrics_event_names.append(ksi.get_names())
                del ksi
        else:
            ks = GPUMetricsSemantic(REPORT_FILE)
            t_metrics = ks.Setup()
            ks.load_data()
            gpu_metrics_agg = ks.get_df()
            metrics_event_names = ks.get_names()
            del ks
        if not t_metrics:
            warn("No GPU metrics information found. Disabling metrics processing.")

    if t_openacc:
        if MULTIREPORT:
            openacc_other_df = []
            openacc_launch_df = []
            openacc_data_df = []
            for REPORT_FILE_I in REPORTS_LIST:
                ksio = OpenACCOtherSemantic(REPORT_FILE_I)
                ksio.Setup()
                ksio.load_data()
                openacc_other_df.append(ksio.get_df())
                ksil = OpenACCLaunchSemantic(REPORT_FILE_I)
                ksil.Setup()
                ksil.load_data()
                openacc_launch_df.append(ksil.get_df())
                ksid = OpenACCDataSemantic(REPORT_FILE_I)
                ksid.Setup()
                ksid.load_data()
                openacc_data_df.append(ksid.get_df())
                del ksio, ksil, ksid
        else:
            kso = OpenACCOtherSemantic(REPORT_FILE)
            kso.Setup()
            kso.load_data()
            openacc_other_df = kso.get_df()
            ksl = OpenACCLaunchSemantic(REPORT_FILE)
            ksl.Setup()
            ksl.load_data()
            openacc_launch_df = ksl.get_df()
            ksd = OpenACCDataSemantic(REPORT_FILE)
            ksd.Setup()
            ksd.load_data()
            openacc_data_df = ksd.get_df()
            del kso, ksl, ksd
        openacc_event_kind = pd.read_sql_table("ENUM_OPENACC_EVENT_KIND", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")


    # MARK: CONTEXT INFO
    list_contexts = []
    list_hostnames = []
    with open(os.path.join(os.path.dirname(__file__), './scripts/gpu-devices-assignment.sql'), 'r') as query:
        t_query = query.read()
        if MULTIREPORT:
            for REPORT_FILE_I in REPORTS_LIST:
                if deviceId_matching_compat:
                    context_info_i = pd.read_sql(t_query, f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE_I)}")
                else:
                    context_info_i = pd.read_sql_table("TARGET_INFO_CUDA_CONTEXT_INFO", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE_I)}")
                    context_info_i['gpuId'] = context_info_i['deviceId']
                target_system_env_i = pd.read_sql_table("TARGET_INFO_SYSTEM_ENV", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE_I)}")
                hostname = target_system_env_i.loc[target_system_env_i["name"] == "Hostname"]["value"].iloc[0]
                context_info_i["hostname"] = hostname
                list_hostnames.append(hostname)
                list_contexts.append(context_info_i)
            context_info = pd.concat(list_contexts)
        else:
            if deviceId_matching_compat:
                context_info = pd.read_sql(t_query, f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")
            else:
                context_info = pd.read_sql_table("TARGET_INFO_CUDA_CONTEXT_INFO", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")
                context_info['gpuId'] = context_info['deviceId']
            target_system_env = pd.read_sql_table("TARGET_INFO_SYSTEM_ENV", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")
            hostname = target_system_env.loc[target_system_env["name"] == "Hostname"]["value"].iloc[0]
            context_info["hostname"] = hostname
    context_info.sort_values(["processId"], inplace=True)

    # CONTEXT INFO CHECK FOR MULTIREPORT
    #if context_info.groupby(["hostname"]).agg({'deviceId': 'count'})
    device_binding_problem = False # See issue #6
    if context_info["deviceId"].unique().size == 1 and context_info.shape[0] > 1:
        device_binding_problem = True
        print(f"\033[93m Warning! Only one unique device ID can be detected in resource identification, but multiple processes. \033[00m")
        if deviceId_matching_compat:
            print(f"\033[93m If translating GPU metrics, the translator will still try to match metric collection with the corresponding device and process with available information. \033[00m")
        else:
            t_metrics = False
            print(f"\033[93m GPU metrics translation is not possible with the current report and nsys version. A solution is provided when using Nsight Systems 2025.1 or greater as backend for exporting. \033[00m")
        print(f"\033[93m However, if this is not intended, we recommend making sure that the GPU bindings are correctly done but still allow to see all devices, and that every process identifies its own GPU with a unique device [0 .. N-1].\n  \033[00m")

    if t_mpi:
        if MULTIREPORT:
            list_ranks = []
            for REPORT_FILE_I in REPORTS_LIST:
                mpi_query = "SELECT globalTid / 0x1000000 % 0x1000000 AS Pid, globalTid % 0x1000000 AS Tid, rank FROM MPI_RANKS;"
                engine = create_engine(f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE_I)}")
                with engine.connect() as conn, conn.begin():
                    list_ranks.append(pd.read_sql_query(mpi_query, conn))
            rank_info = pd.concat(list_ranks)
        else:
            mpi_query = "SELECT globalTid / 0x1000000 % 0x1000000 AS Pid, globalTid % 0x1000000 AS Tid, rank FROM MPI_RANKS;"
            engine = create_engine(f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE)}")
            with engine.connect() as conn, conn.begin():
                rank_info = pd.read_sql_query(mpi_query, conn)

    timings["Import Datasets"] = time.time() - region_start

    # Timing: Merging and aligning
    region_start = time.time()
    # MARK: MERGING AND ALIGNING
    if MULTIREPORT:
        # Find delta between earliest trace start and the others
        session_time = []
        for REPORT_FILE_I in REPORTS_LIST:
            session_time.append(pd.read_sql_table("TARGET_INFO_SESSION_START_TIME", f"sqlite:///{nsi.sqlite_cwd_file(REPORT_FILE_I)}"))
        
        session_time = [x.iloc[0,0] for x in session_time] # Get the utcEpochNs
        earliest_time = reduce(lambda x, y: min(x, y), session_time, float('inf'))
        deltas = [start - earliest_time for start in session_time]

        if t_mpi:
            fmpi = mpi_df[0]
            if not fmpi[fmpi["Event"].str.contains("MPI_Init")].empty: # We can do synchronization via MPI_Init
                ts_init_end = fmpi[fmpi["Event"].str.contains("MPI_Init")].iloc[0]["End:ts_ns"]
                syncs = []

                if t_mpi: # Node synchronization, now limited to MPI
                    for i, df in enumerate(mpi_df):
                        syncs.append((ts_init_end + deltas[0]) - (df[df["Event"].str.contains("MPI_Init")].iloc[0]["End:ts_ns"] + deltas[i]))
                
                deltas = [sum(x) for x in zip(deltas, syncs)]


        for i, df in enumerate(kernels_df):
            df['hostname'] = list_hostnames[i]
            df['Start (ns)'] += deltas[i]
        kernels_df = pd.concat(kernels_df, ignore_index=True)

        if t_graphs:
            for i, df in enumerate(graphs_df):
                df['hostname'] = list_hostnames[i]
                df['start'] += deltas[i]
                df['end'] += deltas[i]
            graphs_df = pd.concat(graphs_df, ignore_index=True)

        if t_apicalls:
            for i, df in enumerate(cuda_api_df):
                df['hostname'] = list_hostnames[i]
                df['Start (ns)'] += deltas[i]

            cuda_api_df = pd.concat(cuda_api_df, ignore_index=True)

        if t_nvtx:
            for i, df in enumerate(nvtx_df):
                df['hostname'] = list_hostnames[i]
                df['Start:ts_ns'] += deltas[i]
                df['End:ts_ns'] += deltas[i]
            nvtx_df = pd.concat(nvtx_df, ignore_index=True)

        if t_nvtx_startend:
            for i, df in enumerate(nvtx_startend_df):
                df['hostname'] = list_hostnames[i]
                df['Start (ns)'] += deltas[i]
                df['End (ns)'] += deltas[i]
            nvtx_startend_df = pd.concat(nvtx_startend_df, ignore_index=True)

        if t_mpi:
            for i, df in enumerate(mpi_df):
                df['hostname'] = list_hostnames[i]
                df['Start:ts_ns'] += deltas[i]
                df['End:ts_ns'] += deltas[i]
            mpi_df = pd.concat(mpi_df, ignore_index=True)
        
        if t_openacc:
            for i, df in enumerate(openacc_other_df):
                df['hostname'] = list_hostnames[i]
                df['start'] += deltas[i]
                df['end'] += deltas[i]
            for i, df in enumerate(openacc_launch_df):
                df['hostname'] = list_hostnames[i]
                df['start'] += deltas[i]
                df['end'] += deltas[i]
            for i, df in enumerate(openacc_data_df):
                df['hostname'] = list_hostnames[i]
                df['start'] += deltas[i]
                df['end'] += deltas[i]
            openacc_other_df = pd.concat(openacc_other_df, ignore_index=True)
            openacc_launch_df = pd.concat(openacc_launch_df, ignore_index=True)
            openacc_data_df = pd.concat(openacc_data_df, ignore_index=True)
        
        if t_metrics:
            for i, df in enumerate(gpu_metrics_agg):
                if not df.empty:
                    df['timestamp'] += deltas[i]
                    # Complement with processId and node info
                    df['Pid'] = df['deviceId'].map(context_info[context_info["hostname"] == list_hostnames[i]].set_index("gpuId")["processId"])
                    df.dropna(subset=['Pid'], inplace=True, ignore_index=True)
                    df['Pid'] = df['Pid'].astype('uint32')
                    df['hostname'] = list_hostnames[i]
            gpu_metrics_agg = pd.concat(gpu_metrics_agg, ignore_index=True)
            metrics_event_names = pd.concat(metrics_event_names, ignore_index=True).drop_duplicates()
    else:
        kernels_df["hostname"] = hostname
        if t_metrics:
            gpu_metrics_agg['Pid'] = gpu_metrics_agg['deviceId'].map(context_info.set_index("gpuId")["processId"])
            gpu_metrics_agg.dropna(subset=['Pid'], inplace=True, ignore_index=True) # If the user has captured metrics for devices that are not in the applications' context, drop them
            gpu_metrics_agg['Pid'] = gpu_metrics_agg['Pid'].astype('uint32')
            gpu_metrics_agg['hostname'] = hostname
        if t_apicalls:
            cuda_api_df['hostname'] = hostname
        if t_nvtx:
            nvtx_df['hostname'] = hostname
        if t_nvtx_startend:
            nvtx_startend_df['hostname'] = hostname
        if t_mpi:
            mpi_df['hostname'] = hostname
        if t_openacc:
            openacc_other_df['hostname'] = hostname
            openacc_launch_df['hostname'] = hostname
            openacc_data_df['hostname'] = hostname
        if t_graphs:
            graphs_df['hostname'] = hostname

    timings["Merging and Aligning"] = time.time() - region_start

    # Timing: Process model
    region_start = time.time()
    # MARK: PROCESS MODEL

    # ## Tasks and threads
    # Now, find unique appearences of ThreadID and ProcessID

    if t_apicalls: print("CUDA calls unique processes: {}, and unique threads: {}".format(cuda_api_df["Pid"].unique(), cuda_api_df["Tid"].unique()))
    if t_nvtx: print("NVTX ranges unique processes: {}, and unique threads: {}".format(nvtx_df["Pid"].unique(), nvtx_df["Tid"].unique()))
    if t_nvtx_startend: print("NVTX startend unique processes: {}, and unique threads: {}".format(nvtx_startend_df["Pid"].unique(), nvtx_startend_df["Tid"].unique()))
    if t_mpi: print("MPI calls unique processes: {}, and unique threads: {}".format(mpi_df["Pid"].unique(), mpi_df["Tid"].unique()))
    if t_openacc: print("OpenACC calls unique processes: {}, and unique threads: {}".format(openacc_other_df["Pid"].unique(), openacc_other_df["Tid"].unique()))
    if t_graphs and graphs_mode == "Node": print("Graphs events unique processes: {}, and unique threads: {}".format(graphs_df["Pid"].unique(), graphs_df["Tid"].unique()))


    compute_threads_with = []
    if t_apicalls: compute_threads_with.append(cuda_api_df[['hostname', 'Pid', 'Tid']])
    if t_nvtx: compute_threads_with.append(nvtx_df[["hostname", "Pid", "Tid"]])
    if t_nvtx_startend: compute_threads_with.append(nvtx_startend_df[["hostname", "Pid", "Tid"]])
    if t_mpi: compute_threads_with.append(mpi_df[["hostname", "Pid", "Tid"]])
    if t_openacc: compute_threads_with.append(openacc_other_df[["hostname", "Pid", "Tid"]])
    if t_graphs and graphs_mode == "Node": compute_threads_with.append(graphs_df[["hostname", "Pid", "Tid"]])

    threads = pd.concat(compute_threads_with, ignore_index=True).drop_duplicates().reset_index(drop=True)
    if t_mpi:
        threads["Rank"] = threads["Pid"].map(rank_info.set_index("Pid")["rank"])
        threads.sort_values(["Rank"], inplace=True)
    else:
        threads.sort_values(["Pid"], inplace=True)
    threads["thread"] = threads.groupby(["Pid"], sort=False).cumcount() + 1
    threads["task"] = threads.groupby(["Pid"], sort=False).ngroup() + 1

    device_mapping = context_info.groupby("processId")["deviceId"].apply(set)
    threads["device"] = threads["Pid"].map(device_mapping)
    threads["device"] = threads["device"].apply(lambda x: x if isinstance(x, set) else set())
    
    #threads.sort_values(["task", "thread"], inplace=True)
    threads.reset_index()
    tasks_set = threads.groupby(["task"], sort=False).agg({'hostname': 'first',
                                            'Pid': 'first',
                                            'Tid': lambda x: set(x),
                                            'thread': 'count',
                                            'device': 'first'})
    print(tasks_set)

    # cuda_api_df["thread"] = 0
    # cuda_api_df["task"] = 0
    # nvtx_df["thread"] = 0
    # nvtx_df["task"] = 0
    # nvtx_startend_df["thread"] = 0
    # nvtx_startend_df["task"] = 0

    # if t_openacc:
    #     openacc_other_df["thread"] = 0
    #     openacc_other_df["task"] = 0
    #     openacc_launch_df["thread"] = 0
    #     openacc_launch_df["task"] = 0
    #     openacc_data_df["thread"] = 0
    #     openacc_data_df["task"] = 0

    threads['row_name'] = "THREAD 1." + threads['task'].astype(str) + '.' + threads['thread'].astype(str)

    # for index,row in cuda_api_df.iterrows():
    #     cuda_api_df.at[index, "thread"] = threads.at[(threads["Tid"] == row["Tid"]).idxmax(), "thread"]
    #     cuda_api_df.at[index, "task"] = threads.at[(threads["Tid"] == row["Tid"]).idxmax(), "task"]

    # for index,row in nvtx_df.iterrows():
    #     nvtx_df.at[index, "thread"] = threads.at[(threads["Tid"] == row["Tid"]).idxmax(), "thread"]
    #     nvtx_df.at[index, "task"] = threads.at[(threads["Tid"] == row["Tid"]).idxmax(), "task"]

    def match_events_with_thread_task(df, threads):
        new_df = df.join(threads.set_index(['Tid', 'hostname'])[["thread", "task"]], on=['Tid', 'hostname'])
        return new_df
    
    if t_apicalls:
        cuda_api_df = match_events_with_thread_task(cuda_api_df, threads)

    if t_nvtx:
        nvtx_df = match_events_with_thread_task(nvtx_df, threads)


    if t_nvtx_startend:
        nvtx_startend_df = match_events_with_thread_task(nvtx_startend_df, threads)

    if t_mpi:
        mpi_df = match_events_with_thread_task(mpi_df, threads)

    if t_openacc:
        openacc_other_df = match_events_with_thread_task(openacc_other_df, threads)
        openacc_launch_df = match_events_with_thread_task(openacc_launch_df, threads)
        openacc_data_df = match_events_with_thread_task(openacc_data_df, threads)
        
    if t_graphs and graphs_mode == "Node":
        graphs_df = match_events_with_thread_task(graphs_df, threads)
    # 
    # ## GPU devices
    # First, detect number of devices and streams.  To respect Paraver's resource model, we will create a THREAD for each stream. To do that, select each unique pair of Device and Stream and assign an incremental ID.

    dfs_streams_to_concat = [kernels_df[['Device', 'Strm', 'deviceid', 'Pid', 'hostname', 'Ctx']]]
    if t_graphs and graphs_mode == "Graph":
        dfs_streams_to_concat.append(graphs_df[['Device', 'Strm', 'deviceid', 'Pid', 'hostname']])
    streams = pd.concat(dfs_streams_to_concat).drop_duplicates().reset_index(drop=True)
    streams["thread"] = streams.sort_values(["Pid", "deviceid", "Strm", "hostname"]).groupby(["Pid", "hostname"]).cumcount() + 1
    #streams["deviceid"] = streams.sort_values("Device").groupby(["Device"]).ngroup()
    #streams["Pid"] = streams["deviceid"].map(tasks_set.set_index("device")["Pid"])
    streams = streams.join(tasks_set.reset_index().set_index(['hostname', 'Pid'])[['task']], on=['hostname', 'Pid'])
    #streams["task"] = streams["Pid"].map(tasks_set.reset_index().set_index("Pid")["task"])
    streams = pd.merge(streams, context_info.reset_index().set_index(['hostname', 'processId', 'contextId'])[['gpuId']], right_index=True, left_on=['hostname', 'Pid', 'Ctx'], how="left", sort=False) # <-- This causes stream replication

    streams['row_name'] = 'CUDA-D'+streams['deviceid'].astype(str) + '.S' + streams['Strm'].astype(str)
    num_streams = streams.count().iloc[0]
    streams.sort_values(["Pid", "thread"], inplace=True)
    streams.reset_index(inplace=True)

    devices_set = streams.groupby(["Pid", "deviceid"]).agg({'Device': 'first',
                                        'Strm': lambda x: set(x),
                                            'thread': 'count',
                                            'task': 'first',
                                            'gpuId': 'first',
                                            'Ctx': 'first'})
    print(devices_set)

    # Here we finally update the threadId we are going to put in the event record of kernel executions to respect the normal threads before CUDA streams

    num_normal_threads = devices_set["task"].map(tasks_set["thread"])
    num_normal_threads_repeated = num_normal_threads.reset_index()["task"].repeat(devices_set["thread"]).reset_index().rename(columns={"task": "thread"})

    streams['thread'] = streams['thread'] + num_normal_threads_repeated["thread"]

    # for index,row in kernels_df.iterrows():
    #     kernels_df.at[index, "thread"] = streams.at[(streams["Strm"] == row["Strm"]).idxmax(), "thread"]
    #     kernels_df.at[index, "deviceid"] = streams.at[(streams["Device"] == row["Device"]).idxmax(), "deviceid"]

    # More efficient way by chatgpt
    # First, let's filter streams DataFrame based on conditions
    filtered_streams = streams.groupby(["Pid", "Strm", 'Ctx']).agg({'thread':'first', 'task':'first'}).reset_index()
    filtered_streams["thread"] = filtered_streams["thread"].apply(int)
    # Now, merge the filtered streams DataFrame with kernels_df
    result_df = kernels_df.merge(filtered_streams, how='left', on=["Pid", 'Strm', 'Ctx'])
    if t_graphs and graphs_mode == "Graph":
        result_2_df = graphs_df.merge(filtered_streams, how='left', on=["Pid", 'Strm'])

    # Copy the results back to kernels_df
    kernels_df['thread'] = result_df['thread'].to_numpy()
    kernels_df['task'] = result_df['task'].to_numpy()
    if t_graphs and graphs_mode == "Graph":
        graphs_df['thread'] = result_2_df['thread'].to_numpy()
        graphs_df['task'] = result_2_df['task'].to_numpy()

    # Add auxiliary stream to streams dataframe
    if t_metrics:
        aux_streams = devices_set.reset_index()[["deviceid", "Device", "thread", "task", "Pid", "gpuId"]]
        aux_streams["Strm"] = 99
        aux_streams["row_name"] = "Metrics GPU"+aux_streams["gpuId"].astype(str)
        #aux_streams["Pid"] = aux_streams["deviceid"].map(tasks_set.set_index('device')["Pid"])
        
        # This line adds the thread number (in Paraver's Process Model indexing) to the metrics helper strings.
        # The result shold correspond to the number of existing threads for that process + the number of existing streams for that process (already in aux_streams["thread"]) + cumulative count for a process
        # aux_streams["Pid"].map(...) does not work for multiple device single process (MDSP), because we need to assign incremental thread index inside one process.
        # Instead of adding just 1, we group the devices by process, and compute the cumulative count on each group. So we end up with the list of devices numbered from 1 to N per PID assigned
        device_count_per_process = devices_set.reset_index().groupby("Pid").cumcount() + 1
        sum_streams_per_process = aux_streams.groupby("Pid").sum()["thread"]
        aux_streams["thread"] = aux_streams["Pid"].map(sum_streams_per_process) + aux_streams["Pid"].map(tasks_set.set_index('Pid')['thread']) + device_count_per_process # This probably does not work when multiple devices are ran by the same process
        gpu_metrics_agg["task"] = gpu_metrics_agg.merge(devices_set.reset_index().set_index(["Pid", "gpuId"])[["task"]], left_on=["Pid", "deviceId"], right_on=["Pid", "gpuId"])["task"]  # <-- This now works with MDSP TODO We need to check if didnt break device per process with faulty ordinal identification
        gpu_metrics_agg["thread"] = gpu_metrics_agg.merge(aux_streams.reset_index().set_index(["Pid", "gpuId"])[["thread"]], left_on=["Pid", "deviceId"], right_on=["Pid", "gpuId"])["thread"]
        streams = pd.concat([streams, aux_streams]).sort_values(['task', 'thread'])



    # ## Writing ROW file
    # Now we can write the _row_ file with this information

    
    print("  -Writing object model to row file...")

    row_df = pd.concat([threads[["thread", "task", "row_name"]], streams[["thread", "task", "row_name"]]])
    row_df.sort_values(["task", "thread"], inplace=True)

    with open(trace_name+".row", "w") as row_file:
        # MISSING NODE INFORMATION, EITHER GET FROM TRACE OR ASK USER
        row_file.write("LEVEL NODE SIZE 1\nnode1\n\n")

        row_file.write("LEVEL THREAD SIZE {}\n".format(len(row_df.index)))
        for index, row in row_df.iterrows():
            row_file.write("{}\n".format(row["row_name"]))

        row_file.write("\n")

    timings["Process Model"] = time.time() - region_start

    # Timing: Event values 
    region_start = time.time()
    # MARK: EVENT NAMES
    # Second step is collect all different event values for CUDA API calls, kernel names, and NVTX ranges.  Each of these define a different event type, and will need unique identifiers to be used as a event values.  Finally these needs to be dumped to the PCF file.

    print("Collecting event names and information...")

    if t_apicalls:
        cuda_api_df["event_value"] = cuda_api_df.groupby(["Name"]).ngroup() + 1
        api_call_names = cuda_api_df[['Name', 'event_value']].drop_duplicates()
        api_call_names.sort_values("event_value", inplace=True)

    # if t_mpi:
    #     mpi_df["event_value"] = mpi_df.groupby(["Event"]).ngroup() + 1
    #     mpi_names = mpi_df[['Event', 'event_value']].drop_duplicates()
    #     mpi_names.sort_values("event_value", inplace=True)
    
    if t_mpi:
        mpi_values = pd.DataFrame.from_dict(MPIVal, orient='index', columns=["event_value"])
        mpi_names = pd.DataFrame.from_dict(MPI_Val_Labels, orient='index', columns=["Name"])
        mpi_names = mpi_names.merge(mpi_values, left_index=True, right_index=True)
        mpi_df["event_value"] = mpi_df["Event"].map(mpi_names.set_index('Name')["event_value"])
        mpi_unknown_values_mask = mpi_df["event_value"].isna()
        df_missing = mpi_df[mpi_unknown_values_mask].copy()
        new_values = (
            df_missing
            .groupby('Event')
            .ngroup()
            .add(1)
            .add(mpi_values["event_value"].max())
        )
        del df_missing
        mpi_df.loc[mpi_unknown_values_mask, "event_value"] = new_values.values
        mpi_df["event_value"] = mpi_df["event_value"].astype('int32')
        to_add = mpi_df.loc[mpi_unknown_values_mask, ['Event', 'event_value']].drop_duplicates().rename(columns={'Event': 'Name'})
        mpi_names = pd.concat([mpi_names, to_add], ignore_index=True)



    kernels_df["event_value"] = kernels_df.groupby(["Name"]).ngroup() + 1 + api_call_names.count().iloc[0] # Add padding to event values so CUDA calls and CUDA kernels can be added
    kernel_names = kernels_df[['event_value', 'Name']].drop_duplicates()
    kernel_names.sort_values("event_value", inplace=True)
    
    # Remove brackets from names
    memops_names = kernel_names.loc[kernel_names["Name"].isin(KernelsSemantic.memops_names) | kernel_names["Name"].str.contains("CUDA memcpy")]
    memops_mask = ~kernel_names.index.isin(memops_names.index)
    kernel_names = kernel_names.loc[memops_mask] #Only keep non-memory kernels names

    memops_names["Name"] = memops_names["Name"].apply(lambda x: x.replace("[", "").replace("]", ""))

    if t_graphs and graphs_mode == "Graph":
        graphs_df["named_event_value"] = graphs_df.groupby(["Name"]).ngroup() + 1 + api_call_names.count().iloc[0] + kernel_names.count().iloc[0] + memops_names.count().iloc[0] # Add padding to event values so CUDA calls and CUDA kernels can be added
        graphs_names = graphs_df[['named_event_value', "Name"]].drop_duplicates()
        graphs_names.sort_values("named_event_value", inplace=True)
    if t_graphs and graphs_mode == "Node":
            kernels_df["graphNodeId"] = kernels_df["graphNodeId"].apply(lambda x: int(0) if pd.isna(x) else int(x)) # Sets kernels in_graph flag if contain a value for the graphNodeId column
    
    # # Split of kernel execution between compute and memory

    memops_df = kernels_df.loc[kernels_df["Name"].isin(KernelsSemantic.memops_names) | kernels_df["Name"].str.contains("CUDA memcpy")]
    memops_mask = ~kernels_df.index.isin(memops_df.index)
    kernels_df = kernels_df.loc[memops_mask] #Only keep non-memory kernels
    memops_df["bytes_b"] = memops_df["bytes_b"].astype("str", copy=True).apply(lambda x: int(locale.atof(x))).astype("int")
    
    # Extract NCCL kernels
    nccl_df = kernels_df.loc[kernels_df["Name"].str.contains("nccl")]
    mask = ~kernels_df.index.isin(nccl_df.index)
    kernels_df = kernels_df.loc[mask]

    nccl_kernel_names = kernel_names.loc[kernel_names["Name"].str.contains("nccl")]
    mask = ~kernel_names.index.isin(nccl_kernel_names.index)
    kernel_names = kernel_names.loc[mask]

    if t_nvtx:
        nvtx_df_subset = nvtx_df.reset_index()
        # lower_level = max(nvtx_df["Lvl"])

        # if nvtx_select_frames:
        #     #subset of df
        #     nvtx_df_subset = nvtx_df[(nvtx_df["Lvl"] >= nvtx_stack_top) & (nvtx_df["Lvl"] <= nvtx_stack_bottom)]

        # split NCCL events
        nvtx_nccl_df = nvtx_df_subset[nvtx_df_subset["domain"] == "NCCL"].copy().reset_index(drop=True)
        nvtx_df_subset = nvtx_df_subset.drop(nvtx_df_subset[nvtx_df_subset["domain"] == "NCCL" ].index)
        nvtx_nccl_df["event_type"] = event_type_nvtx_nccl

        if t_nccl:
            nvtx_nccl_df["jsonText"] = nvtx_nccl_df["jsonText"].apply(lambda s: json.loads(s) if(pd.notna(s)) else '')
            json_expanded = pd.json_normalize(nvtx_nccl_df["jsonText"]).set_index(nvtx_nccl_df.index)
            json_expanded['payload_valid'] = json_expanded.notna().any(axis='columns')
            nvtx_nccl_df = pd.concat([nvtx_nccl_df.drop(columns=['jsonText']), json_expanded], axis=1)
            ## Create dictionary of events for generic payload

            # Step 1: Extract column names as event names and assign event type numbers
            nccl_payload_event_dict = {col: 9501 + i for i, col in enumerate(json_expanded.columns)}
            nccl_payload_event_dict = pd.DataFrame({
                "Name": list(nccl_payload_event_dict.keys()),
                "type": list(nccl_payload_event_dict.values())
            })

            # Step 2: Identify non-numerical columns and create DataFrames for their unique values
            non_numeric_nccl_payloads = {}

            for col in json_expanded.select_dtypes(include='object').columns:
                nvtx_nccl_df[f"{col}_value"] = nvtx_nccl_df.groupby(col, dropna=True).ngroup() + 1
                nvtx_nccl_df[f"{col}_value"] = nvtx_nccl_df[f"{col}_value"].fillna(0).apply(int)
                unique_values = nvtx_nccl_df[[col, f"{col}_value"]].dropna().drop_duplicates()
                #unique_values = json_expanded[col].dropna().unique()
                non_numeric_nccl_payloads[col] = pd.DataFrame({
                    f"event_name": unique_values[col].tolist(),
                    f"event_value": unique_values[f"{col}_value"].tolist()
                })
                nvtx_nccl_df[col] = nvtx_nccl_df[f"{col}_value"]


        # Now recurring domains, starting with nesmik
        if not nvtx_df_subset.empty:
            nvtx_df_subset.loc[nvtx_df_subset["domain"] == "neSmiK", "event_type"] = event_type_nvtx_nesmik
            nvtx_df_subset["event_type"] = (nvtx_df_subset[nvtx_df_subset["domain"] != "neSmiK"].sort_values("domain").groupby(["domain"]).ngroup() * 100) + event_type_nvtx_base
            nvtx_df_subset.loc[nvtx_df_subset["domain"] == "", "domain"] = "default"

            nvtx_df_subset["event_value"] = nvtx_df_subset.groupby(["Name"]).ngroup() + 1
            #nvtx_df_subset["event_value"] = nvtx_df_subset["RangeId"]
            domain_names = nvtx_df_subset[["event_type", "domain"]].drop_duplicates()
            
            domains_dict = []
            for i, r in domain_names.iterrows():
                domains_dict.append({"name": r["domain"], "type": r["event_type"], "names": nvtx_df_subset.loc[nvtx_df_subset["domain"] == r["domain"], ['event_value', 'Name']].drop_duplicates().sort_values("event_value")})

            ranges_names = nvtx_df_subset[['event_value', 'Name']].drop_duplicates()
            ranges_names.sort_values("event_value", inplace=True)
        else:
            warn("No other NVTX ranges found part from NCCL.")

        # Now nccl treating
        if not nvtx_nccl_df.empty:
            nvtx_nccl_df["event_value"] = nvtx_nccl_df.groupby(["Name"]).ngroup() + 1
            nccl_names = nvtx_nccl_df[['event_value', 'Name']].drop_duplicates().sort_values("event_value")
            nccl_names["Name"] = nccl_names["Name"].apply(lambda x: x.split(':', 1)[1])

    if t_nvtx_startend:
        nvtx_startend_df["event_value"] = nvtx_startend_df.groupby(["tag"]).ngroup() + 1
        nvtx_startend_names = nvtx_startend_df[['tag', 'event_value']].drop_duplicates()
        nvtx_startend_names.sort_values("event_value", inplace=True)
        nvtx_startend_names

    if t_openacc:
        openacc_event_kind["id"] += 1
        openacc_launch_df["eventKind"] += 1
        openacc_data_df["eventKind"] += 1
        openacc_other_df["eventKind"] += 1

        openacc_data_df["name_value"] = openacc_data_df.groupby(["name"], dropna=False).ngroup() + 1
        openacc_full_data_names = openacc_data_df[['name_value', 'name']].drop_duplicates()
        openacc_full_data_names.sort_values(["name_value"], inplace=True)

        openacc_launch_df["name_value"] = openacc_launch_df.groupby(["name"], dropna=False).ngroup() + 1 + openacc_full_data_names.count().iloc[0]
        openacc_full_launch_names = openacc_launch_df[['name_value', 'name']].drop_duplicates()
        openacc_full_launch_names.sort_values(["name_value"], inplace=True)

        openacc_other_df["name_value"] = openacc_other_df.groupby(["name"], dropna=False).ngroup() + 1 + openacc_full_data_names.count().iloc[0] + openacc_full_launch_names.count().iloc[0]
        openacc_full_other_names = openacc_other_df[['name_value', 'name']].drop_duplicates()
        openacc_full_other_names.sort_values(["name_value"], inplace=True)

        openacc_data_df["func_value"] = openacc_data_df.groupby(["func"], dropna=False).ngroup() + 1
        openacc_full_data_funcs = openacc_data_df[['func_value', 'func']].drop_duplicates()
        openacc_full_data_funcs.sort_values(["func_value"], inplace=True)

        openacc_launch_df["func_value"] = openacc_launch_df.groupby(["func"], dropna=False).ngroup() + 1 + openacc_full_data_funcs.count().iloc[0]
        openacc_full_launch_funcs = openacc_launch_df[['func_value', 'func']].drop_duplicates()
        openacc_full_launch_funcs.sort_values(["func_value"], inplace=True)

        openacc_other_df["func_value"] = openacc_other_df.groupby(["func"], dropna=False).ngroup() + 1 + openacc_full_data_funcs.count().iloc[0] + openacc_full_launch_funcs.count().iloc[0]
        openacc_full_other_funcs = openacc_other_df[['func_value', 'func']].drop_duplicates()
        openacc_full_other_funcs.sort_values(["func_value"], inplace=True)



    print("-\tWriting pcf file...")

    with open(trace_name+".pcf", "w") as pcf_file:

        CONFIG = """
DEFAULT_OPTIONS

LEVEL               THREAD
UNITS               NANOSEC
LOOK_BACK           100
SPEED               1
FLAG_ICONS          ENABLED
NUM_OF_STATE_COLORS 1000
YMAX_SCALE          37


DEFAULT_SEMANTIC

THREAD_FUNC          State As Is

GRADIENT_COLOR
0    {0,255,2}
1    {0,244,13}
2    {0,232,25}
3    {0,220,37}
4    {0,209,48}
5    {0,197,60}
6    {0,185,72}
7    {0,173,84}
8    {0,162,95}
9    {0,150,107}
10    {0,138,119}
11    {0,127,130}
12    {0,115,142}
13    {0,103,154}
14    {0,91,166}


GRADIENT_NAMES
0    Gradient 0
1    Grad. 1/MPI Events
2    Grad. 2/OMP Events
3    Grad. 3/OMP locks
4    Grad. 4/User func
5    Grad. 5/User Events
6    Grad. 6/General Events
7    Grad. 7/Hardware Counters
8    Gradient 8
9    Gradient 9
10    Gradient 10
11    Gradient 11
12    Gradient 12
13    Gradient 13
14    Gradient 14

        """

        pcf_file.write(CONFIG)

        if t_apicalls:
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} CUDA library call\n".format(event_type_api))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in api_call_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
            pcf_file.write("\n")

        if t_mpi:
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} {}\n".format(MPITYPE_PTOP, MPI_Type_Labels["MPITYPE_PTOP"]))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in mpi_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
            pcf_file.write("\n")
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} {}\n".format(MPITYPE_COLLECTIVE, MPI_Type_Labels["MPITYPE_COLLECTIVE"]))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in mpi_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
            pcf_file.write("\n")
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} {}\n".format(MPITYPE_OTHER, MPI_Type_Labels["MPITYPE_OTHER"]))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in mpi_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
            pcf_file.write("\n")
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} {}\n".format(MPITYPE_RMA, MPI_Type_Labels["MPITYPE_RMA"]))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in mpi_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
            pcf_file.write("\n")
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} {}\n".format(MPITYPE_IO, MPI_Type_Labels["MPITYPE_IO"]))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in mpi_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
            pcf_file.write("\n")
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("1 {} {}\n".format(MPITYPE_SEND_GLOBAL_SIZE, "Send Size in MPI Global OP"))
            pcf_file.write("1 {} {}\n".format(MPITYPE_RECV_GLOBAL_SIZE, "Recv Size in MPI Global OP"))
            pcf_file.write("\n")

        pcf_file.write("EVENT_TYPE\n")
        pcf_file.write("0 {} CUDA kernel\n".format(KernelsSemantic.event_type_kernels))
        pcf_file.write("VALUES\n")
        pcf_file.write("0 End\n")
        for index, row in kernel_names.iterrows():
            pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
        pcf_file.write("\n")

        pcf_file.write("EVENT_TYPE\n")
        pcf_file.write("0 {} CUDA memcpy kernel\n".format(KernelsSemantic.event_type_memcpy))
        pcf_file.write("VALUES\n")
        pcf_file.write("0 End\n")
        for index, row in memops_names.iterrows():
            pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
        pcf_file.write("\n")

        pcf_file.write("EVENT_TYPE\n")
        pcf_file.write("0 {} NCCL kernel\n".format(KernelsSemantic.event_type_nccl_kernels))
        pcf_file.write("VALUES\n")
        pcf_file.write("0 End\n")
        for index, row in nccl_kernel_names.iterrows():
            pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
        pcf_file.write("\n")

        pcf_file.write("EVENT_TYPE\n")
        for i, v in enumerate(KernelsSemantic.event_types_block_grid_values_names):
            pcf_file.write("0 {} Kernel {}\n".format(KernelsSemantic.event_types_block_grid_values[i], v))
        pcf_file.write("0 {} Kernel Registers/Thread\n".format(KernelsSemantic.event_type_registers_thread))
        pcf_file.write("0 {} Memcopy size\n".format(KernelsSemantic.event_type_memcopy_size))
        pcf_file.write("0 {} Correlation ID\n".format(KernelsSemantic.event_type_correlation))
        pcf_file.write("\n")

        if t_graphs:
            if graphs_mode == "Graph":
                pcf_file.write("EVENT_TYPE\n")
                pcf_file.write("0 {} CUDA Graphs Exec name\n".format(CUDAGraphsSemantic.cuda_graph_execution_named))
                pcf_file.write("VALUES\n")
                pcf_file.write("0 End\n")
                for index, row in graphs_names.iterrows():
                    pcf_file.write("{} {}\n".format(row["named_event_value"], row["Name"]))
                pcf_file.write("\n")
                pcf_file.write("EVENT_TYPE\n")
                pcf_file.write("0 {} CUDA Graphs ID\n".format(CUDAGraphsSemantic.cuda_graph_id))
                pcf_file.write("0 {} CUDA Graphs Exec ID\n".format(CUDAGraphsSemantic.cuda_graph_exec_id))
            elif graphs_mode == "Node":
                pcf_file.write("0 {} Graph Node ID\n".format(CUDAGraphsSemantic.cuda_graph_node_id))

            

        if t_metrics:
            pcf_file.write("EVENT_TYPE\n")
            for i, r in metrics_event_names.iterrows():
                pcf_file.write("7 {} {}\n".format(r["metricId"], r["metricName"]))
            pcf_file.write("\n")

        if t_nvtx:
            if not nvtx_df_subset.empty:
                for i, v in enumerate(domains_dict):
                    pcf_file.write("EVENT_TYPE\n")
                    pcf_file.write("0 {} NVTX pushpop ranges {} domain\n".format(v["type"], v["name"]))
                    pcf_file.write("VALUES\n")
                    pcf_file.write("0 End\n")
                    for index, row in v["names"].iterrows():
                        pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
                    pcf_file.write("\n")
            if not nvtx_nccl_df.empty:
                pcf_file.write("EVENT_TYPE\n")
                pcf_file.write("0 {} NCCL regions\n".format(event_type_nvtx_nccl))
                pcf_file.write("VALUES\n")
                pcf_file.write("0 End\n")
                for index, row in nccl_names.iterrows():
                    pcf_file.write("{} {}\n".format(row["event_value"], row["Name"]))
                pcf_file.write("\n")
                if t_nccl:
                    for i, v in nccl_payload_event_dict.iterrows():
                        pcf_file.write("EVENT_TYPE\n")
                        pcf_file.write("0 {} NCCL {}\n".format(v["type"], v["Name"]))
                        if v["Name"] in non_numeric_nccl_payloads:
                            pcf_file.write("VALUES\n")
                            pcf_file.write("0 End\n")
                            for index, row in non_numeric_nccl_payloads[v["Name"]].iterrows():
                                pcf_file.write("{} {}\n".format(row["event_value"], row["event_name"]))
                            pcf_file.write("\n")
                        pcf_file.write("\n")
                    pcf_file.write("\n")

        if t_nvtx_startend:
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} NVTX startend ranges\n".format(event_type_nvtx_startend))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in nvtx_startend_names.iterrows():
                pcf_file.write("{} {}\n".format(row["event_value"], row["tag"]))

        if t_openacc:
            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC Data Events\n".format(event_type_openacc_data))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_event_kind.iterrows():
                pcf_file.write("{} {}\n".format(row["id"], row["label"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC Launch Events\n".format(event_type_openacc_launch))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_event_kind.iterrows():
                pcf_file.write("{} {}\n".format(row["id"], row["label"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC Other Events\n".format(event_type_openacc))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_event_kind.iterrows():
                pcf_file.write("{} {}\n".format(row["id"], row["label"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC data region source\n".format(event_type_name_openacc_data))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_full_data_names.iterrows():
                pcf_file.write("{} {}\n".format(row["name_value"], row["name"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC launch region source\n".format(event_type_name_openacc_launch))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_full_launch_names.iterrows():
                pcf_file.write("{} {}\n".format(row["name_value"], row["name"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC other region source\n".format(event_type_name_openacc))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_full_other_names.iterrows():
                pcf_file.write("{} {}\n".format(row["name_value"], row["name"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC data function name\n".format(event_type_func_openacc_data))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_full_data_funcs.iterrows():
                pcf_file.write("{} {}\n".format(row["func_value"], row["func"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC launch function name\n".format(event_type_func_openacc_launch))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_full_launch_funcs.iterrows():
                pcf_file.write("{} {}\n".format(row["func_value"], row["func"]))
            pcf_file.write("\n")

            pcf_file.write("EVENT_TYPE\n")
            pcf_file.write("0 {} OpenACC other function name\n".format(event_type_func_openacc))
            pcf_file.write("VALUES\n")
            pcf_file.write("0 End\n")
            for index, row in openacc_full_other_funcs.iterrows():
                pcf_file.write("{} {}\n".format(row["func_value"], row["func"]))
            pcf_file.write("\n")

    timings["Event Values"] = time.time() - region_start

    # Timing: Memory and comms
    region_start = time.time()
    # MARK: MEMORY AND COMMUNICATIONS
    
    # # Communications
    # ## Correlation lines
    # CUDA API calls - Kernels
    comm_kernel_df = cuda_api_df.merge(kernels_df, how="inner", left_on=["CorrID", "task"], right_on=["CorrID", "task"], suffixes=("_call", "_k"))

    if t_graphs:
        if graphs_mode == "Graph":
            # CUDA API calls - Graphs
            comm_api_graph_df = cuda_api_df.merge(graphs_df, how="inner", left_on=["CorrID", "task"], right_on=["CorrID", "task"], suffixes=("_call", "_k"))
        elif graphs_mode == "Node":
            pass # Here to implement correlation of node events with their corresponding cuda calls

    # CUDA API calls - memory operations
    comm_memory_df = cuda_api_df.merge(memops_df, how="inner", left_on=["CorrID", "task"], right_on=["CorrID", "task"], suffixes=("_call", "_mem"))

    # CUDA API calls - NCCL kernels
    comm_nccl_df = cuda_api_df.merge(nccl_df, how="inner", left_on=["CorrID", "task"], right_on=["CorrID", "task"], suffixes=("_call", "_k"))
    comm_kernel_df = pd.concat([comm_kernel_df,comm_nccl_df], ignore_index=True)

    # # NCCL Payloads
    if t_nccl:
        partial_searches = []
        for ti in tasks_set.index:
            # Define function to find the CorrID for events in B contained within events in A
            def find_corr_id(df_A_task, df_B_task):
                in_group = False
                idx_group = 0
                corr_ids = pd.Series(index=df_A_task.index)
                for idx, row in df_A_task.iterrows():
                    #print(idx)
                    # Filter DataFrame B for events that satisfy the conditions
                    if row["Name"] == "NCCL:ncclGroupStart":
                        in_group = True
                        corr_ids.loc[idx] = np.nan
                        continue
                    elif row["Name"] == "NCCL:ncclGroupEnd":
                        corr_ids.loc[idx] = np.nan
                        in_group = False
                        idx_group = 0
                    else:
                        if in_group:
                            if idx_group == 0: # search for next end
                                next_end = df_A_task[(df_A_task["Name"] == "NCCL:ncclGroupEnd") & (df_A_task["thread"] == row["thread"]) & (df_A_task["Start:ts_ns"] > row["Start:ts_ns"])]
                                closing_end = next_end[next_end["Start:ts_ns"] == next_end["Start:ts_ns"].min()].iloc[0]
                                filtered_group = df_B_task[(df_B_task["Start (ns)"] >= closing_end["Start:ts_ns"]) &
                                                    (df_B_task["Start (ns)"] < (closing_end["End:ts_ns"])) &
                                                    (df_B_task["thread"] == closing_end["thread"])]
                                filtered_group = filtered_group.sort_values("Start (ns)").reset_index(drop=True)
                            #print(idx)
                            corr_ids.loc[idx] = filtered_group["CorrID"].iloc[idx_group]
                            idx_group = idx_group + 1
                        else:
                            filtered_B = df_B_task[
                                (df_B_task["Start (ns)"] >= row["Start:ts_ns"]) &
                                (df_B_task["Start (ns)"] < (row["End:ts_ns"])) &
                                (df_B_task["thread"] == row["thread"])
                            ]
                            if not filtered_B.empty:
                                corr_ids.loc[idx] = filtered_B["CorrID"].iloc[0]
                            else:
                                corr_ids.loc[idx] = np.nan
                return corr_ids

            # Apply the function to each row of DataFrame A
            df_A_task = nvtx_nccl_df[(nvtx_nccl_df["task"] == ti)]
            df_B_task = cuda_api_df[(cuda_api_df["Name"].str.contains("LaunchKernel")) & (cuda_api_df["task"] == ti)]

            new_corr_ids = find_corr_id(df_A_task, df_B_task=df_B_task)
            partial_searches.append(new_corr_ids)

        nvtx_nccl_df["CorrID"] = pd.concat(partial_searches)
        nccl_df = nccl_df.merge(nvtx_nccl_df[nccl_payload_event_dict["Name"].tolist() + ["CorrID"]], how="left", on="CorrID") # <- If we get CoddID null here, means that event search was not successful


    timings["Memory and comms"] = time.time() - region_start

    # Timing: Timeline reconstruction
    region_start = time.time()
    # MARK: TIMELINE RECONS
    # # Timeline reconstruction

    print("Reconstructing timeline...")

    def create_event_record(start, dur, thread, task, type, value):
        begin = "2:0:1:{}:{}:{}:{}:{}\n".format(task, thread, start, type, value)
        end   = "2:0:1:{}:{}:{}:{}:{}\n".format(task, thread, start+dur, type, 0)
        return begin+end

    def create_combined_events_record(start, dur, thread, task, types, values):
        begin = "2:0:1:{}:{}:{}".format(task, thread, start)
        end   = "2:0:1:{}:{}:{}".format(task, thread, start+dur)
        for i, v in enumerate(types):
            begin = begin + ":{}:{}".format(v, values[i])
            end = end + ":{}:{}".format(v, 0)
        begin = begin + "\n"
        end = end + "\n"
        return begin+end

    def create_communication_record(from_task, from_thread, to_task, to_thread, time_send, time_rcv, size, tag):
        obj_send = "0:1:{0}:{1}".format(
            from_task, from_thread
        )
        obj_recv = "0:1:{0}:{1}".format(
            to_task, to_thread
        )
        return "3:"+obj_send+":{time_send}:{time_send}:".format(time_send = time_send) + obj_recv + ":{time_rcv}:{time_rcv}:{size}:{tag}\n".format(time_rcv = time_rcv, size = size, tag = tag)

    def create_metrics_record(metric_row):
        base = "2:0:1:{}:{}:{}".format(metric_row["task"], metric_row["thread"], metric_row["timestamp"])
        event_values = ""
        for pair in zip(metric_row["metricId"], metric_row["value"]):
            event_values += ":{}:{}".format(pair[0], pair[1])
        base += event_values
        base += "\n"
        return base

    now = time.strftime("%d/%m/%Y at %H:%M")

    applist = "{}:(".format(len(tasks_set.index))
    for i, r in row_df.groupby(["task"]).count().iterrows():
        applist = applist + "{}:1".format(r["thread"])
        if i < len(tasks_set.index): applist = applist + ","
    applist = applist + ")"

    compute_max_with = []
    if t_apicalls: compute_max_with.append((cuda_api_df["Start (ns)"] + cuda_api_df["Duration (ns)"]).max())
    if t_nvtx: compute_max_with.append(nvtx_df["End:ts_ns"].max())
    if t_nvtx_startend: compute_max_with.append(nvtx_startend_df["end"].max())
    if t_mpi: compute_max_with.append(mpi_df["End:ts_ns"].max())

    ftime = max(compute_max_with)
    header = "#Paraver ({}):{}_ns:0:1:{}\n".format(now, ftime, applist)

    written_events = []
    with open(trace_name+".prv", "w") as prv_file:
        prv_file.write(header)

        # Write events


        if t_graphs and graphs_mode == "Node":
            written_events.append(kernels_df.shape[0])
            types = [KernelsSemantic.event_type_kernels] + KernelsSemantic.event_types_block_grid_values + [KernelsSemantic.event_type_registers_thread, KernelsSemantic.event_type_correlation, CUDAGraphsSemantic.cuda_graph_node_id]
            ewr(prv_file, kernels_df, "Kernels", lambda r:
                    (create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types, [r["event_value"]] + [int(r['GrdX']), int(r['GrdY']), int(r['GrdZ']), int(r['BlkX']), int(r['BlkY']), int(r['BlkZ']), int(r['StcSMem:mem_B']), int(r['DymSMem:mem_B']), int(r['localMemoryTotal']), int(r['Reg/Trd']), r["CorrID"], r["graphNodeId"]])))
        else:
            written_events.append(kernels_df.shape[0])
            types = [KernelsSemantic.event_type_kernels] + KernelsSemantic.event_types_block_grid_values + [KernelsSemantic.event_type_registers_thread, KernelsSemantic.event_type_correlation]
            ewr(prv_file, kernels_df, "Kernels", lambda r:
                        (create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types, [r["event_value"]] + [int(r['GrdX']), int(r['GrdY']), int(r['GrdZ']), int(r['BlkX']), int(r['BlkY']), int(r['BlkZ']), int(r['StcSMem:mem_B']), int(r['DymSMem:mem_B']), int(r['localMemoryTotal']), int(r['Reg/Trd']), r["CorrID"]])))

        if t_graphs and graphs_mode == "Graph":
            written_events.append(graphs_df.shape[0])
            types = [CUDAGraphsSemantic.cuda_graph_execution_named, CUDAGraphsSemantic.cuda_graph_id, CUDAGraphsSemantic.cuda_graph_exec_id]
            ewr(prv_file, graphs_df, "CUDA Graphs", lambda r:
                    (create_combined_events_record(r['start'], r['end']-r['start'], int(r["thread"]), int(r["task"]), types, [r["named_event_value"], r["graphId"], r["graphExecId"]])))

        if t_nccl:
            def ser_nccl_kernels(r):
                valid = [pd.notna(r[rowname]) for rowname in nccl_payload_event_dict["Name"].tolist()]
                valid_payload = nccl_payload_event_dict[valid]
                types = [KernelsSemantic.event_type_nccl_kernels] + KernelsSemantic.event_types_block_grid_values + [KernelsSemantic.event_type_registers_thread, KernelsSemantic.event_type_correlation] + valid_payload["type"].tolist()
                return create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types, [r["event_value"]] + [int(r['GrdX']), int(r['GrdY']), int(r['GrdZ']), int(r['BlkX']), int(r['BlkY']), int(r['BlkZ']), int(r['StcSMem:mem_B']), int(r['DymSMem:mem_B']), int(r['localMemoryTotal']), int(r['Reg/Trd']), r["CorrID"]] + [int(r[rowname]) for rowname in valid_payload["Name"].tolist()])

            ewr(prv_file, nccl_df, "NCCL Kernels",  ser_nccl_kernels)
        else:
            written_events.append(nccl_df.shape[0])
            types = [KernelsSemantic.event_type_nccl_kernels] + KernelsSemantic.event_types_block_grid_values + [KernelsSemantic.event_type_registers_thread, KernelsSemantic.event_type_correlation]
            ewr(prv_file, nccl_df, "NCCL Kernels", lambda r:
                (create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types, [r["event_value"]] + [int(r['GrdX']), int(r['GrdY']), int(r['GrdZ']), int(r['BlkX']), int(r['BlkY']), int(r['BlkZ']), int(r['StcSMem:mem_B']), int(r['DymSMem:mem_B']), int(r['localMemoryTotal']), int(r['Reg/Trd']), r["CorrID"]])))

        if t_graphs and graphs_mode == "Node":
            written_events.append(memops_df.shape[0])
            types_mem = [KernelsSemantic.event_type_memcpy, KernelsSemantic.event_type_memcopy_size, KernelsSemantic.event_type_correlation, CUDAGraphsSemantic.cuda_graph_node_id]
            ewr(prv_file, memops_df, "Memory operations", lambda r: 
                    (create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types_mem, [r["event_value"], r["bytes_b"], r["CorrID"], r["graphNodeId"]])))
        else:
            written_events.append(memops_df.shape[0])
            types_mem = [KernelsSemantic.event_type_memcpy, KernelsSemantic.event_type_memcopy_size, KernelsSemantic.event_type_correlation]
            ewr(prv_file, memops_df, "Memory operations", lambda r: 
                        (create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types_mem, [r["event_value"], r["bytes_b"], r["CorrID"]])))

        if t_apicalls:
            written_events.append(cuda_api_df.shape[0])
            types_api = [event_type_api, KernelsSemantic.event_type_correlation]
            ewr(prv_file, cuda_api_df, "CUDA API calls", lambda r:
                        (create_combined_events_record(r.iloc[0], r.iloc[1], int(r["thread"]), int(r["task"]), types_api, [r["event_value"], r["CorrID"]])))


        if t_nvtx:
            if not nvtx_df_subset.empty:
                ewr(prv_file, nvtx_df_subset, "NVTX pushpop ranges", lambda r:
                            (create_event_record(r["Start:ts_ns"], r["Duration:dur_ns"], int(r["thread"]), int(r["task"]), r["event_type"], r["event_value"])))
            # NVTX NCCL regions, still missing nccl info
            if not nvtx_nccl_df.empty:
                ewr(prv_file, nvtx_nccl_df, "NVTX NCCL regions", lambda r:
                    (create_event_record(r["Start:ts_ns"], r["Duration:dur_ns"], int(r["thread"]), int(r["task"]), r["event_type"], r["event_value"])))

        if t_nvtx_startend:
            ewr(prv_file, nvtx_startend_df, "NVTX startend ranges", lambda r:
                        (create_event_record(r["start"], r["duration"], int(r["thread"]), int(r["task"]), event_type_nvtx_startend, r["event_value"])))


        if t_mpi:
            def serialize_mpi(r):
                if r["Kind"] == "collectives":
                    return create_combined_events_record(r.iloc[1], r.iloc[3], int(r["thread"]), int(r["task"]), [r["event_type"], MPITYPE_SEND_GLOBAL_SIZE, MPITYPE_RECV_GLOBAL_SIZE], [r["event_value"], r["CollSendSize:mem_b"], r["CollRecvSize:mem_b"]])
                else:
                    return create_event_record(r.iloc[1], r.iloc[3], int(r["thread"]), int(r["task"]), r["event_type"], r["event_value"])
            ewr(prv_file, mpi_df, "MPI events", lambda r: serialize_mpi(r))

        if t_openacc:
            t_acc_d = [event_type_openacc_data, event_type_name_openacc_data, event_type_func_openacc_data, event_type_openacc_data_size]
            ewr(prv_file, openacc_data_df, "OpenACC data constructs", lambda r:
                        (create_combined_events_record(r["start"], r["end"] - r["start"], r["thread"], r["task"], t_acc_d, [r["eventKind"], r["name_value"], r["func_value"], r["bytes"]])))
            t_acc_l = [event_type_openacc_launch, event_type_name_openacc_launch, event_type_func_openacc_launch]
            ewr(prv_file, openacc_launch_df, "OpenACC launch constructs", lambda r:
                        (create_combined_events_record(r["start"], r["end"] - r["start"], r["thread"], r["task"], t_acc_l, [r["eventKind"], r["name_value"], r["func_value"]])))
            t_acc_o = [event_type_openacc, event_type_name_openacc, event_type_func_openacc]
            ewr(prv_file, openacc_other_df, "OpenACC other constructs", lambda r:
                        (create_combined_events_record(r["start"], r["end"] - r["start"], r["thread"], r["task"], t_acc_o, [r["eventKind"], r["name_value"], r["func_value"]])))

        if t_metrics:
            ewr(prv_file, gpu_metrics_agg, "GPU metrics", lambda r:
                        (create_metrics_record(r)))

        if t_apicalls:
            ewr(prv_file, comm_kernel_df, "API-Kernel correlation lines", lambda r:
                        (create_communication_record(r["task"], r["thread_call"], r["task"], r["thread_k"], (r["Start (ns)_call"]), r["Start (ns)_k"], 0, comm_tag_launch)))
            ewr(prv_file, comm_memory_df, "API-Memory correlation lines", lambda r:
                        (create_communication_record(r["task"], r["thread_call"], r["task"], r["thread_mem"], (r["Start (ns)_call"]), r["Start (ns)_mem"], int(r["bytes_b"]), comm_tag_memory)))
            if t_graphs and graphs_mode == "Graph":
                ewr(prv_file, comm_api_graph_df, "API-Graphs correlation lines", lambda r:
                        (create_communication_record(r["task"], r["thread_call"], r["task"], r["thread_k"], (r["Start (ns)"]), r["start"], 0, comm_tag_launch)))


    # Timing: Postprocessing
    region_start = time.time()
    # MARK: POSTPROCESSING
    # ## Postprocessing
    # - Reorder trace
    # - GZip trace

    print(f"Congratulations! Trace is written to {trace_name}.prv")
    print("Postprocessing...")

    if args.sort:
        print("- Sorting trace...")
        args_sorter = (PARAVER_HOME+"/bin/sort-trace.awk.sh", trace_name+".prv")
        print(args_sorter)
        with subprocess.Popen(args_sorter, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
            for line in p.stdout: 
                print(line.decode(), end='')

        if p.returncode != 0:
            raise ChildProcessError(p.returncode, p.args)
        
        os.remove(trace_name+".prv")
        os.remove(trace_name+".pcf")
        os.remove(trace_name+".row")

    if args.compress:
        print("- Compressing trace...")
        if args.sort:
            args_gzip = ("gzip", trace_name+".sorted.prv")
        else:
            args_gzip = ("gzip", trace_name+".prv")
        print(args_gzip)
        with subprocess.Popen(args_gzip, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
            for line in p.stdout: 
                print(line.decode(), end='')

        if p.returncode != 0:
            raise ChildProcessError(p.returncode, p.args)

    timings["Postprocessing"] = time.time() - region_start

    # End timing the entire execution
    total_execution_time = time.time() - start_time
    timings["Total Execution"] = total_execution_time

    # Calculate the number of reports and total events
    num_reports = len(REPORTS_LIST) if MULTIREPORT else 1
    total_events = sum(written_events)

    # Write timings to CSV
    if args.timing:
        write_timings_to_csv(timings, num_reports, total_events)
        print(f"Timings written to {TIMINGS_CSV_FILE}")

if __name__ == "__main__":
    main()
