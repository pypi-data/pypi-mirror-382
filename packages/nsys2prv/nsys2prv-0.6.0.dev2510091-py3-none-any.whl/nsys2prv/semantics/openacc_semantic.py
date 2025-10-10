from .nsys_event import NsysEvent
import os.path
from sqlalchemy import text

class OpenACCOtherSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        with open(os.path.join(os.path.dirname(__file__), '../scripts/openacc_other.sql'), 'r') as query:
            self.query = text(query.read())
    
class OpenACCLaunchSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        with open(os.path.join(os.path.dirname(__file__), '../scripts/openacc_launch.sql'), 'r') as query:
            self.query = text(query.read())

class OpenACCDataSemantic(NsysEvent):
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        with open(os.path.join(os.path.dirname(__file__), '../scripts/openacc_data.sql'), 'r') as query:
            self.query = text(query.read())