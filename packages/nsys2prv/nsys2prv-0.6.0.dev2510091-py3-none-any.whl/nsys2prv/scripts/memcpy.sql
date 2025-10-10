SELECT
    start AS "start",
    (end - start) AS "duration",
    NULL AS "gridX",
    NULL AS "gridY",
    NULL AS "gridZ",
    NULL AS "blockX",
    NULL AS "blockY",
    NULL AS "blockZ",
    NULL AS "regsperthread",
    NULL AS "ssmembytes",
    NULL AS "dsmembytes",
    NULL as "localMemoryTotal",
    bytes AS "bytes",
    msrck.label AS "srcmemkind",
    mdstk.label AS "dstmemkind",
    NULL AS "memsetval",
    printf('%s (%d)', gpu.name, deviceId) AS "device",
    deviceId as "deviceId",
    contextId AS "context",
    greenContextId AS "greenContext",
    streamId AS "stream",
    '[CUDA memcpy ' || memopstr.label || ']' AS "name",
    correlationId AS "correlation",
    globalPid / 0x1000000 % 0x1000000 AS PID,
    coalesce(graphNodeId, NULL) as "graphNodeId"
FROM
    CUPTI_ACTIVITY_KIND_MEMCPY AS memcpy
LEFT JOIN
    ENUM_CUDA_MEMCPY_OPER AS memopstr
    ON memcpy.copyKind == memopstr.id
LEFT JOIN
    ENUM_CUDA_MEM_KIND AS msrck
    ON memcpy.srcKind == msrck.id
LEFT JOIN
    ENUM_CUDA_MEM_KIND AS mdstk
    ON memcpy.dstKind == mdstk.id
LEFT JOIN
    TARGET_INFO_GPU AS gpu
    ON memcpy.deviceId == gpu.id