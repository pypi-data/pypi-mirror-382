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
    mk.label AS "srcmemkind",
    NULL AS "dstmemkind",
    value AS "memsetval",
    printf('%s (%d)', gpu.name, deviceId) AS "device",
    deviceId as "deviceId",
    contextId AS "context",
    greenContextId AS "greenContext",
    streamId AS "stream",
    '[CUDA memset]' AS "name",
    correlationId AS "correlation",
    globalPid / 0x1000000 % 0x1000000 AS PID,
    coalesce(graphNodeId, NULL) as graphNodeId
FROM
    CUPTI_ACTIVITY_KIND_MEMSET AS memset
LEFT JOIN
    ENUM_CUDA_MEM_KIND AS mk
    ON memset.memKind == mk.id
LEFT JOIN
    TARGET_INFO_GPU AS gpu
    ON memset.deviceId == gpu.id