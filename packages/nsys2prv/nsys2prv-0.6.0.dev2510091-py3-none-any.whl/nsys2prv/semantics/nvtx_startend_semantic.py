from .nsys_event import NsysEvent
import os.path
from sqlalchemy import text

class NVTXStartEndSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        with open(os.path.join(os.path.dirname(__file__), '../scripts/nvtx_startend_trace.sql'), 'r') as query:
            self.query = text(query.read())

    def _preprocess(self):
        self._df["domain"] = self._df["tag"].str.split(":").str[0]
        return super()._preprocess()