SELECT
    CASE
        WHEN srcFile NOT NULL
            THEN nameIds.value || '@' || srcFileIds.value || ':' || lineNo
        ELSE nameIds.value
    END AS name,
    start,
    end,
    eventKind,
    funcIds.value as func,
    globalTid / 0x1000000 % 0x1000000 AS Pid, globalTid % 0x1000000 AS Tid
FROM
    CUPTI_ACTIVITY_KIND_OPENACC_OTHER
LEFT JOIN
    StringIds AS srcFileIds
    ON srcFileIds.id == srcFile
LEFT JOIN
    StringIds AS nameIds
    ON nameIds.id == nameId
LEFT JOIN
    StringIds AS funcIds
    ON funcIds.id == funcName