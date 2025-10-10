from .nsys_event import NsysEvent
import os.path
from .mpi_event_encoding import *
from sqlalchemy import text
import pandas as pd

class MPIP2PSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        if self.check_table('MPI_P2P_EVENTS') and self.check_table('MPI_START_WAIT_EVENTS'):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/mpi_p2p.sql'), 'r') as query:
                self.query = text(query.read())
        else:
            self._empty = True
            return False
    def _preprocess(self):
        self._df["event_type"] = MPITYPE_PTOP
        return super()._preprocess()
    
    def postprocess(self):
        if not self._empty:
            start_wait_mask = self._df["Kind"].eq("startwait")
            df_to_process = self._df[start_wait_mask].copy()
            self._df = self._df.drop(self._df.index[start_wait_mask])
            one_wait = df_to_process.groupby(["Start:ts_ns", "End:ts_ns", "Pid", "Tid"]).head(1) # Now we only keep one appearance. Future implementations can put requestHandles in a set and use them.
            self._df = pd.concat([self._df, one_wait])

        return super().postprocess()

class MPICollSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        if self.check_table("MPI_COLLECTIVES_EVENTS"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/mpi_coll.sql'), 'r') as query:
                self.query = text(query.read())
        else:
            self._empty = True
    
    def _preprocess(self):
        self._df = self._df.drop(self._df[self._df["Event"].str.contains("File") ].index)
        self._df["event_type"] = MPITYPE_COLLECTIVE

class MPIOtherSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        if self.check_table("MPI_OTHER_EVENTS"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/mpi_other.sql'), 'r') as query:
                self.query = text(query.read())
        else:
            self._empty = True
    
    def _preprocess(self):
        self._df = self._df.drop(self._df[self._df["Event"].str.contains("File") ].index)
        self._df = self._df.drop(self._df[self._df["Event"].str.contains("Win|MPI_Get|MPI_Put|Accumulate") ].index)
        self._df["event_type"] = MPITYPE_OTHER

class MPIRMASemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        if self.check_table("MPI_OTHER_EVENTS"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/mpi_other.sql'), 'r') as query:
                self.query = text(query.read())
        else:
            self._empty = True
    def _preprocess(self):
        self._df = self._df[self._df["Event"].str.contains("Win|MPI_Get|MPI_Put|Accumulate")]
        self._df["event_type"] = MPITYPE_RMA

class MPIIOPSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        if self.check_table("MPI_OTHER_EVENTS") and self.check_table("MPI_COLLECTIVES_EVENTS"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/mpi_io.sql'), 'r') as query:
                self.query = text(query.read())
        else:
            self._empty = True
    
    def _preprocess(self):
        self._df = self._df[self._df["Event"].str.contains("File")]
        self._df["event_type"] = MPITYPE_IO
        self._df["Kind"] = "io"
