SELECT
    CASE
        WHEN srcFile NOT NULL
            THEN nameIds.value || '@' || srcFileIds.value || ':' || lineNo
        ELSE nameIds.value
    END AS name,
    start,
    end,
    eventKind,
    varIds.value as variableName,
    funcIds.value as func,
    bytes,
    globalTid / 0x1000000 % 0x1000000 AS Pid, globalTid % 0x1000000 AS Tid
FROM
    CUPTI_ACTIVITY_KIND_OPENACC_DATA
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
    StringIds AS varIds
    ON varIds.id == varName