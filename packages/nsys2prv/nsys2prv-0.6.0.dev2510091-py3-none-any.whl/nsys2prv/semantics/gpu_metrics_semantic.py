from .nsys_event import NsysEvent
from pandas import read_sql_table, DataFrame
from sqlalchemy import text

event_type_metrics_base = 9400


class GPUMetricsSemantic(NsysEvent):
    def __init__(self, report) -> None:
        self.metrics_event_names = DataFrame()
        super().__init__(report)
    
    def Setup(self):
        if self.check_table("GPU_METRICS"):
            self.query = text("SELECT * FROM GPU_METRICS")
            return True
        else:
            self._empty = True
            return False
    
    def _preprocess(self):
        metrics_description = read_sql_table("TARGET_INFO_GPU_METRICS", self._dbcon)
        self._df.drop(self._df[self._df["timestamp"] < 0].index, inplace=True) # drop negative time
        self.metrics_event_names = metrics_description.groupby(["metricId"]).agg({'metricName': 'first'}).reset_index()
        self.metrics_event_names["metricId"] = self.metrics_event_names["metricId"] + event_type_metrics_base
        self._df["deviceId"] = self._df["typeId"].apply(lambda x: x & 0xFF)
        self._df.loc[self._df["value"] < 0, "value"] = 0 # Workaround for bug #33 (https://gitlab.pm.bsc.es/beppp/nsys2prv/-/issues/33)
        self._df = self._df.groupby(["timestamp", "typeId"]).agg({'metricId': lambda x: list(x+event_type_metrics_base),
                                                                        'value': lambda x: list(x),
                                                                        'deviceId': 'first'})
        self._df.reset_index(inplace=True)
        return super()._preprocess()
    
    def get_names(self):
        return self.metrics_event_names