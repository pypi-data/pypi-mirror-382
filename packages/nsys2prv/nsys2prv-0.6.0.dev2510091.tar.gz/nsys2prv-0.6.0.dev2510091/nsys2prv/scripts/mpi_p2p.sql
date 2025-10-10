WITH
    evts AS (
		SELECT
            'p2p' AS source,
            start AS start,
            end AS end,
            globalTid AS globalTid,
            textId AS textId,
            size AS size,
            NULL AS collSendSize,
            NULL AS collRecvSize,
            tag AS tag,
            remoteRank AS remoteRank,
            NULL AS rootRank
        FROM
            MPI_P2P_EVENTS
			UNION ALL
			        SELECT
            'startwait' AS source,
            start AS start,
            end AS end,
            globalTid AS globalTid,
            textId AS textId,
            NULL AS size,
            NULL AS collSendSize,
            NULL AS collRecvSize,
            NULL AS tag,
            NULL AS remoteRank,
            NULL AS rootRank
        FROM
            MPI_START_WAIT_EVENTS
    )
SELECT
	e.source as "Kind",
    e.start AS "Start:ts_ns",
    e.end AS "End:ts_ns",
    e.end - e.start AS "Duration:dur_ns",
    s.value AS "Event",
    (e.globalTid >> 24) & 0x00FFFFFF AS "Pid",
    e.globalTid & 0x00FFFFFF AS "Tid",
    e.tag AS "Tag",
    r.rank AS "Rank",
    e.remoteRank AS "PeerRank",
    e.rootRank AS "RootRank",
    e.size AS "Size:mem_b",
    e.collSendSize AS "CollSendSize:mem_b",
    e.collRecvSize AS "CollRecvSize:mem_b"
FROM
    evts AS e
LEFT JOIN
    StringIds AS s
    ON e.textId == s.id
LEFT JOIN
    MPI_RANKS AS r
    ON e.globalTid == r.globalTid
ORDER BY 1
;