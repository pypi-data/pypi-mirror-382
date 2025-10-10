WITH RECURSIVE
    tree AS (
        SELECT
            p.rangeId AS rangeId,
            ':' || CAST(p.rangeId AS TEXT) AS rangeIdHier,
            p.parentId AS parentId,
            0 AS level,
            '' AS tab
        FROM
            temp.NVTX_PARENT AS p
        WHERE p.parentId IS NULL

        UNION ALL
        SELECT
            p.rangeId AS rangeId,
            tree.rangeIdHier || ':' || CAST(p.rangeId AS TEXT) AS rangeIdHier,
            p.parentId AS parentId,
            tree.level + 1 AS level,
            tree.tab || '--' AS tab
        FROM
            tree
        JOIN
            temp.NVTX_PARENT AS p
            ON p.parentId == tree.rangeId

        ORDER BY level DESC
    )
SELECT
    ne.start AS "Start:ts_ns",
    ne.start + p.duration AS "End:ts_ns",
    p.duration AS "Duration:dur_ns",
    ifnull(p.childDuration, 0) AS "DurChild:dur_ns",
    p.duration - ifnull(p.childDuration, 0) AS "DurNonChild:dur_ns",
    p.fullname AS "Name",
    (ne.globalTid >> 24) & 0x00FFFFFF AS "PID",
    ne.globalTid & 0x00FFFFFF AS "TID",
    t.level AS "Lvl",
    ifnull(p.childNumb, 0) AS "NumChild",
    ne.rowid AS "RangeId",
    t.parentId AS "ParentId",
    t.rangeIdHier AS "RangeStack",
    t.tab || p.fullname AS "NameTree",
    ne.jsonText
FROM
    NVTX_EVENTS AS ne
JOIN
    temp.NVTX_PARENT AS p
    ON p.rangeId == ne.rowid
JOIN
    tree AS t
    ON t.rangeId == ne.rowid
ORDER BY 1, 3