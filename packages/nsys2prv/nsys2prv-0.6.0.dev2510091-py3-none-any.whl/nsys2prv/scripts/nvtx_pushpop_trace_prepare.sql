DROP TABLE IF EXISTS temp.NVTX_EVENTS_MINMAXTS;

CREATE TEMP TABLE NVTX_EVENTS_MINMAXTS
AS SELECT
    min(min(start), min(end)) AS min,
    max(max(start), max(end)) AS max
FROM NVTX_EVENTS
WHERE
       eventType == 59
    OR eventType == 70;


DROP TABLE IF EXISTS temp.NVTX_EVENTS_RIDX;


CREATE VIRTUAL TABLE temp.NVTX_EVENTS_RIDX
USING rtree
(
    rangeId,
    startTS,
    endTS,
    +startNS   INTEGER,
    +endNS     INTEGER,
    +tid       INTEGER
);

INSERT INTO temp.NVTX_EVENTS_RIDX
    SELECT
        e.rowid AS rangeId,
        rtree_scale(e.start,
            (SELECT min FROM temp.NVTX_EVENTS_MINMAXTS),
            (SELECT max FROM temp.NVTX_EVENTS_MINMAXTS)) AS startTS,
        rtree_scale(ifnull(e.end, (SELECT max FROM temp.NVTX_EVENTS_MINMAXTS)),
            (SELECT min FROM temp.NVTX_EVENTS_MINMAXTS),
            (SELECT max FROM temp.NVTX_EVENTS_MINMAXTS)) AS endTS,
        e.start AS startNS,
        ifnull(e.end, (SELECT max FROM temp.NVTX_EVENTS_MINMAXTS)) AS endNS,
        e.globalTid AS tid
    FROM
        NVTX_EVENTS AS e
    WHERE
           e.eventType == 59
        OR e.eventType == 70;

DROP TABLE IF EXISTS temp.NVTX_PARENT;


CREATE TEMP TABLE NVTX_PARENT (
    rangeId         INTEGER PRIMARY KEY   NOT NULL,
    parentId        INTEGER,
    duration        INTEGER,
    childDuration   INTEGER,
    childNumb       INTEGER,
    fullname        TEXT
);

INSERT INTO temp.NVTX_PARENT
    WITH
        domains AS (
            SELECT
                min(ne.start),
                ne.domainId AS id,
                ne.globalTid AS globalTid,
                coalesce(sid.value, ne.text) AS name
            FROM
                NVTX_EVENTS AS ne
            LEFT JOIN
                StringIds AS sid
                ON ne.textId == sid.id
            WHERE
                ne.eventType == 75
            GROUP BY 2, 3
        )
    SELECT
        ne.rowid AS rangeId,
        NULL AS parentId,
        ifnull(ne.end, (SELECT max FROM temp.NVTX_EVENTS_MINMAXTS)) - ne.start AS duration,
        0 AS childDuration,
        0 AS childNumb,
        coalesce(d.name, '') || ':' || coalesce(sid.value, ne.text, '') AS fullname

    FROM
        NVTX_EVENTS AS ne
    LEFT JOIN
        domains AS d
        ON ne.domainId == d.id
            AND (ne.globalTid & 0x0000FFFFFF000000) == (d.globalTid & 0x0000FFFFFF000000)
    LEFT JOIN
        StringIds AS sid
        ON ne.textId == sid.id
    WHERE
           ne.eventType == 59
        OR ne.eventType == 70;

UPDATE temp.NVTX_PARENT SET parentId = child.pid
FROM (
    SELECT
        cr.rangeId as cid,
        pr.rangeId as pid,
        min((cr.startNS - pr.startNS) + (pr.endNS - cr.EndNS)) as tightness
    FROM
        temp.NVTX_EVENTS_RIDX AS cr
    JOIN
        temp.NVTX_EVENTS_RIDX AS pr
    ON
        pr.rangeId != cr.rangeId
        AND pr.startTS <= cr.startTS
        AND pr.endTS >= cr.endTS
        AND pr.startNS <= cr.startNS
        AND pr.endNS >= cr.endNS
        AND pr.tid == cr.tid
    GROUP BY cid
) AS child
WHERE temp.NVTX_PARENT.rangeId = child.cid;

UPDATE temp.NVTX_PARENT
    SET (childDuration, childNumb) = (totals.cDur, totals.cNum)
FROM (
    SELECT
        parentId AS pId,
        total(duration) AS cDur,
        count(*) AS cNum
    FROM
        temp.NVTX_PARENT
    GROUP BY 1
) AS totals
WHERE temp.NVTX_PARENT.rangeId == totals.pId;

CREATE INDEX IF NOT EXISTS temp.NVTX_PARENT__PARENTID
    ON NVTX_PARENT (parentId);