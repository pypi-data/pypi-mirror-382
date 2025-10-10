from .nsys_event import NsysEvent
from sqlalchemy import text
import os.path


class CUDAGraphsSemantic(NsysEvent):

    cuda_graph_execution_named = 63_000_008 # To display with the rest of the CUDA Activities along with kernels
    cuda_graph_id = 63_000_100
    cuda_graph_exec_id = 63_000_101
    cuda_graph_node_id = 63_000_102
    tracing_mode = ""

    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        trace_mode_capture = self.get_value("META_DATA_CAPTURE", "name", "PROCESS_0:CUDA_GRAPH_TRACE_OPTIONS:MODE")
        if not trace_mode_capture.empty:
            self.tracing_mode = trace_mode_capture["value"].iloc[0]

        if self.tracing_mode == "Node":
            if self.check_table("CUDA_GRAPH_NODE_EVENTS"):
                with open(os.path.join(os.path.dirname(__file__), '../scripts/graph_node.sql'), 'r') as query:
                    self.query = text(query.read())
                return True
            else:
                self._empty = True
                self.tracing_mode = ""
                return False
        else:
            if self.check_table("CUPTI_ACTIVITY_KIND_GRAPH_TRACE"):
                with open(os.path.join(os.path.dirname(__file__), '../scripts/graph_cupti.sql'), 'r') as query:
                    self.query = text(query.read())
                return True
            else:
                self._empty = True
                self.tracing_mode = ""
                return False
    
    def _preprocess(self):
        self._df.reset_index(inplace=True)
        return super()._preprocess()
