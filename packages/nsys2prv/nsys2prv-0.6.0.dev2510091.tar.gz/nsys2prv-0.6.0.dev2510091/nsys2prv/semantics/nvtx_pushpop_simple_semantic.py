from .nsys_event import NsysEvent
import os.path
from sqlalchemy import text

class NVTXPushPopSimpleSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        with open(os.path.join(os.path.dirname(__file__), '../scripts/nvtx_pushpop_simple.sql'), 'r') as query:
            self.query = text(query.read())

    def _preprocess(self):
        self._df["domain"] = self._df["Name"].str.split(":").str[0]
        self._df.rename(columns={"PID":"Pid", "TID":"Tid"}, inplace=True)
        return super()._preprocess()