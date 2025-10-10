SELECT 
	start AS "start",
	(end - start) AS "duration",
	gridX AS "gridX",
	gridY AS "gridY",
	gridZ AS "gridZ",
	blockX AS "blockX",
	blockY AS "blockY",
	blockZ AS "blockZ",
	registersPerThread AS "regsperthread",
	staticSharedMemory AS "ssmembytes",
	dynamicSharedMemory AS "dsmembytes",
	localMemoryTotal as "localMemoryTotal",
	NULL AS "bytes",
	NULL AS "srcmemkind",
	NULL AS "dstmemkind",
	NULL AS "memsetval",
	printf('%s (%d)', gpu.name, deviceId) AS "device",
	deviceId as "deviceId",
	contextId AS "context",
	greenContextId AS "greenContext",
	streamId AS "stream",
	str.value AS "name",
	correlationId AS "correlation",
	globalPid / 0x1000000 % 0x1000000 AS PID,
	coalesce(graphNodeId, NULL) as "graphNodeId"
FROM
	CUPTI_ACTIVITY_KIND_KERNEL AS kern
LEFT JOIN
	TARGET_INFO_GPU AS gpu
	ON gpu.id == kern.deviceId
LEFT JOIN
	StringIds as str
	ON str.id == kern.shortName