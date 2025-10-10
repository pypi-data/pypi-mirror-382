import pandas as pd

class ProcessModel:

    class MissingDatabaseFile(Exception):
        def __init__(self, filename):
            super().__init__(f'Database file {filename} does not exist.')

    PID_COL = "Pid"
    TID_COL = "Tid"
    HOSTNAME_COL = "hostname"

    K_STREAM_COL = "Strm"

    with_mpi = False
    context_info = pd.DataFrame()
    
    threads = pd.DataFrame()
    tasks_set = pd.DataFrame()
    streams = pd.DataFrame()
    devices_set = pd.DataFrame()

    def __init__(self, context_info, pid_col="Pid", tid_col="Tid", hn_col="hostname", with_mpi=False) -> None:
        self.PID_COL = pid_col
        self.TID_COL = tid_col
        self.HOSTNAME_COL = hn_col
        self.with_mpi = with_mpi

        self.context_info = context_info

    def match_events_with_thread_task(self, df):
        new_df = df.join(self.threads.set_index([self.TID_COL, self.HOSTNAME_COL])[["thread", "task"]], on=[self.TID_COL, self.HOSTNAME_COL])
        return new_df
    
    def compute_task_set(self, types):
        compute_threads_with = [df_set[[self.HOSTNAME_COL, self.TID_COL, self.PID_COL]] for df_set in types]
        threads = pd.concat(compute_threads_with, ignore_index=True).drop_duplicates().reset_index(drop=True)

        threads["thread"] = threads.groupby(["Pid"], sort=False).cumcount() + 1
        threads["task"] = threads.groupby(["Pid"], sort=False).ngroup() + 1

        device_mapping = self.context_info.groupby("processId")["deviceId"].apply(set)
        threads["device"] = threads["Pid"].map(device_mapping)
        threads["device"] = threads["device"].apply(lambda x: x if isinstance(x, set) else set())
        
        threads.reset_index()
        self.tasks_set = threads.groupby(["task"], sort=False).agg({'hostname': 'first',
                                                'Pid': 'first',
                                                'Tid': lambda x: set(x),
                                                'thread': 'count',
                                                'device': 'first'})
        threads['row_name'] = "THREAD 1." + threads['task'].astype(str) + '.' + threads['thread'].astype(str)
        self.threads = threads

    def compute_device_set(self, types):
        dfs_streams_to_concat = [dfs[['Device', 'Strm', 'deviceid', self.PID_COL, self.HOSTNAME_COL, 'Ctx']] for dfs in types]
        streams = pd.concat(dfs_streams_to_concat).drop_duplicates().reset_index(drop=True)
        streams["thread"] = streams.sort_values(["Pid", "deviceid", "Strm", "hostname"]).groupby(["Pid", "hostname"]).cumcount() + 1
        #streams["deviceid"] = streams.sort_values("Device").groupby(["Device"]).ngroup()
        #streams["Pid"] = streams["deviceid"].map(tasks_set.set_index("device")["Pid"])
        streams = streams.join(self.tasks_set.reset_index().set_index(['hostname', 'Pid'])[['task']], on=['hostname', 'Pid'])
        #streams["task"] = streams["Pid"].map(tasks_set.reset_index().set_index("Pid")["task"])
        streams = pd.merge(streams, self.context_info.reset_index().set_index(['hostname', 'processId', 'contextId'])[['gpuId']], right_index=True, left_on=['hostname', 'Pid', 'Ctx'], how="left", sort=False) # <-- This causes stream replication

        streams['row_name'] = 'CUDA-D'+streams['deviceid'].astype(str) + '.S' + streams['Strm'].astype(str)
        num_streams = streams.count().iloc[0]
        streams.sort_values(["Pid", "thread"], inplace=True)
        streams.reset_index(inplace=True)

        self.devices_set = streams.groupby(["Pid", "deviceid"]).agg({'Device': 'first',
                                            'Strm': lambda x: set(x),
                                                'thread': 'count',
                                                'task': 'first',
                                                'gpuId': 'first',
                                                'Ctx': 'first'})
        num_normal_threads = self.devices_set["task"].map(self.tasks_set["thread"])
        num_normal_threads_repeated = num_normal_threads.reset_index()["task"].repeat(self.devices_set["thread"]).reset_index().rename(columns={"task": "thread"})
        streams['thread'] = streams['thread'] + num_normal_threads_repeated["thread"]
        self.streams = streams

    def set_kernel_thread_id(self, df) -> pd.DataFrame:
        filtered_streams = self.streams.groupby(["Pid", "Strm", 'Ctx']).agg({'thread':'first', 'task':'first'}).reset_index()
        filtered_streams["thread"] = filtered_streams["thread"].apply(int)
        # Now, merge the filtered streams DataFrame with kernels_df
        result_df = df.merge(filtered_streams, how='left', on=["Pid", 'Strm', 'Ctx'])

        # Copy the results back to kernels_df
        df['thread'] = result_df['thread'].to_numpy()
        df['task'] = result_df['task'].to_numpy()
        del result_df
        return df
    
    def add_auxiliary_for_metrics(self, metrics_df) -> pd.DataFrame:
        aux_streams = self.devices_set.reset_index()[["deviceid", "Device", "thread", "task", "Pid"]]
        aux_streams["Strm"] = 99
        aux_streams["row_name"] = "Metrics GPU"+aux_streams["deviceid"].astype(str)
        #aux_streams["Pid"] = aux_streams["deviceid"].map(tasks_set.set_index('device')["Pid"])
        
        # This line adds the thread number (in Paraver's Process Model indexing) to the metrics helper strings.
        # The result shold correspond to the number of existing threads for that process + the number of existing streams for that process (already in aux_streams["thread"]) + cumulative count for a process
        # aux_streams["Pid"].map(...) does not work for multiple device single process (MDSP), because we need to assign incremental thread index inside one process.
        # Instead of adding just 1, we group the devices by process, and compute the cumulative count on each group. So we end up with the list of devices numbered from 1 to N per PID assigned
        device_count_per_process = self.devices_set.reset_index().groupby("Pid").cumcount() + 1
        sum_streams_per_process = aux_streams.groupby("Pid").sum()["thread"]
        aux_streams["thread"] = aux_streams["Pid"].map(sum_streams_per_process) + aux_streams["Pid"].map(self.tasks_set.set_index('Pid')['thread']) + device_count_per_process # This probably does not work when multiple devices are ran by the same process
        self.streams = pd.concat([self.streams, aux_streams]).sort_values(['task', 'thread'])
        
        metrics_df["task"] = metrics_df.merge(self.devices_set.reset_index().set_index(["Pid", "gpuId"])[["task"]], left_on=["Pid", "deviceId"], right_on=["Pid", "gpuId"])["task"]  # <-- This now works with MDSP TODO We need to check if didnt break device per process with faulty ordinal identification
        metrics_df["thread"] = metrics_df.merge(aux_streams.reset_index().set_index(["Pid", "deviceid"])[["thread"]], left_on=["Pid", "deviceId"], right_on=["Pid", "deviceid"])["thread"]
        return metrics_df
    
    def get_task_set(self):
        return self.tasks_set
    
    def get_device_set(self):
        return self.devices_set