WITH
    openacc AS (
        SELECT
            start,
            end,
            nameId,
            eventKind,
            lineNo,
            srcFile,
            globalTid,
            bytes,
			funcName
        FROM CUPTI_ACTIVITY_KIND_OPENACC_DATA
        UNION ALL 
        SELECT
            start,
            end,
            nameId,
            eventKind,
            lineNo,
            srcFile,
            globalTid,
			null AS bytes,
            funcName
        FROM CUPTI_ACTIVITY_KIND_OPENACC_LAUNCH
        UNION ALL
        SELECT
            start,
            end,
            nameId,
            eventKind,
            lineNo,
            srcFile,
            globalTid,
			null AS bytes,
			null AS funcName
        FROM CUPTI_ACTIVITY_KIND_OPENACC_OTHER
    )
SELECT
    CASE
        WHEN srcFile NOT NULL
            THEN nameIds.value || '@' || srcFileIds.value || ':' || lineNo
        ELSE nameIds.value
    END AS name,
    start,
    end,
    eventIds.label,
	funcIds.value as func,
	bytes,
    globalTid / 0x1000000 % 0x1000000 AS Pid, globalTid % 0x1000000 AS Tid
FROM
    openacc
LEFT JOIN
    StringIds AS srcFileIds
    ON srcFileIds.id == srcFile
LEFT JOIN
    StringIds AS nameIds
    ON nameIds.id == nameId
LEFT JOIN
	StringIds AS funcIds
	ON funcIds.id == funcName
LEFT JOIN
	ENUM_OPENACC_EVENT_KIND as eventIds
	ON eventIds.id == eventKind