from .nsys_event import NsysEvent
import os.path
from sqlalchemy import text

class KernelsSemantic(NsysEvent):
    event_type_kernels = 63000006
    event_type_memcpy = 63000001
    event_type_memcopy_size = 63000002
    event_types_block_grid_values = [9101, 9102, 9103, 9104, 9105, 9106, 9107, 9108, 9109]
    event_types_block_grid_values_names = ['GrdX', 'GrdY', 'GrdZ', 'BlkX', 'BlkY', 'BlkZ', 'Static Shared Memory', 'Dynamic Shared Memory', 'Local memory reserved for kernel']
    event_type_registers_thread = 9110
    event_type_correlation = 9200
    event_type_nccl_kernels = 63000007
    memops_names = ["[CUDA memcpy Device-to-Device]", "[CUDA memcpy Device-to-Host]", "[CUDA memcpy Host-to-Device]", "[CUDA memset]", "[CUDA memcpy Peer-to-Peer]"]

    
    def __init__(self, report) -> None:
        super().__init__(report)
    
    def Setup(self):
        subset_tables = []
        base_query = """
            WITH recs AS (
                {subset_tables_q}
            )
            SELECT
                start AS "Start (ns)",
                duration AS "Duration:dur_ns",
                correlation AS "CorrID",
                gridX AS "GrdX",
                gridY AS "GrdY",
                gridZ AS "GrdZ",
                blockX AS "BlkX",
                blockY AS "BlkY",
                blockZ AS "BlkZ",
                regsperthread AS "Reg/Trd",
                ssmembytes AS "StcSMem:mem_B",
                dsmembytes AS "DymSMem:mem_B",
                localMemoryTotal as "localMemoryTotal",
                bytes AS "bytes_b",
                CASE
                    WHEN bytes IS NULL
                        THEN NULL
                    ELSE
                        bytes * (1000000000 / duration)
                END AS "Throughput:thru_B",
                srcmemkind AS "SrcMemKd",
                dstmemkind AS "DstMemKd",
                device AS "Device",
                deviceId as "deviceid",
                PID AS "Pid",
                context AS "Ctx",
                NULLIF(greenContext, 0) AS "GreenCtx",
                stream AS "Strm",
                name AS "Name",
                graphNodeId
            FROM recs
            ORDER BY start;
        """
        union = """
            UNION ALL
        """

        if self.check_table("CUPTI_ACTIVITY_KIND_KERNEL"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/kernels.sql'), 'r') as query:
                subset_tables.append(query.read())
        if self.check_table("CUPTI_ACTIVITY_KIND_MEMCPY"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/memcpy.sql'), 'r') as query:
                subset_tables.append(query.read())
        if self.check_table("CUPTI_ACTIVITY_KIND_MEMSET"):
            with open(os.path.join(os.path.dirname(__file__), '../scripts/memset.sql'), 'r') as query:
                subset_tables.append(query.read())
        
        if len(subset_tables) == 0:
            self._empty = True

        self.query = text(base_query.format(subset_tables_q = union.join(subset_tables)))