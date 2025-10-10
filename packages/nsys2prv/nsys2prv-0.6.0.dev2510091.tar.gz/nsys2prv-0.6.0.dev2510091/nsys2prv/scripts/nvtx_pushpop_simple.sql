WITH
    domains AS (
        SELECT
            min(start),
            domainId AS id,
            globalTid AS globalTid,
            text AS name
        FROM
            NVTX_EVENTS
        WHERE
            eventType == 75
        GROUP BY 2, 3
    ),
    maxts AS(
        SELECT max(max(start), max(end)) AS m
        FROM   NVTX_EVENTS
    ),
    nvtx AS (
        SELECT
			ne.start AS "Start:ts_ns",
            ne.end AS "End:ts_ns",
            coalesce(ne.end, (SELECT m FROM maxts)) - ne.start AS "Duration:dur_ns",
            CASE
                WHEN d.name NOT NULL AND sid.value IS NOT NULL
                    THEN d.name || ':' || sid.value
                WHEN d.name NOT NULL AND sid.value IS NULL
                    THEN d.name || ':' || ne.text
                WHEN d.name IS NULL AND sid.value NOT NULL
                    THEN ':' || sid.value
                ELSE ':' || ne.text
            END AS "Name",
            ne.jsonText,
			(ne.globalTid / 0x1000000 % 0x1000000) as PID,
			(ne.globalTid % 0x1000000) as TID
        FROM
            NVTX_EVENTS AS ne
        LEFT OUTER JOIN
            domains AS d
            ON ne.domainId == d.id
                AND (ne.globalTid & 0x0000FFFFFF000000) == (d.globalTid & 0x0000FFFFFF000000)
        LEFT OUTER JOIN
            StringIds AS sid
            ON ne.textId == sid.id
        WHERE
            ne.eventType == 59
            OR
            ne.eventType == 70
    )
SELECT
	*
	FROM
	nvtx