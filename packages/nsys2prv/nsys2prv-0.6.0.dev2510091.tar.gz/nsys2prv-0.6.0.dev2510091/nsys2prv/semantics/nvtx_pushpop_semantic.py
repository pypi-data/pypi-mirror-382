from .nsys_event import NsysEvent
import os.path
from sqlalchemy import text

class NVTXPushPopSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        with open(os.path.join(os.path.dirname(__file__), '../scripts/nvtx_pushpop_trace_prepare.sql'), 'r') as query:
            for statement in query.read().split(';'):
                if len(statement.strip()) > 0:
                    self.prepare_statements.append(statement)
        with open(os.path.join(os.path.dirname(__file__), '../scripts/nvtx_pushpop_trace.sql'), 'r') as query:
            self.query = text(query.read())

    def _preprocess(self):
        self._df["domain"] = self._df["Name"].str.split(":").str[0]
        self._df.rename(columns={"PID":"Pid", "TID":"Tid"}, inplace=True)
        return super()._preprocess()