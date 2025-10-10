SELECT
    e.start,
    e.globalPid,
    e.deviceId,
    e.contextId,
    HEX(e.address),
    e.bytes,
    memKind.label AS memKindName,
    memOper.label AS memoryOperationTypeName,
    e.name AS variableName,
    e.streamId,
    e.localMemoryPoolAddress,
    e.localMemoryPoolReleaseThreshold,
    e.localMemoryPoolSize,
    e.localMemoryPoolUtilizedSize,
    e.importedMemoryPoolAddress,
    e.importedMemoryPoolProcessId,
	e.globalPid / 0x1000000 % 0x1000000 AS PID
FROM
    CUDA_GPU_MEMORY_USAGE_EVENTS e
LEFT JOIN
    ENUM_CUDA_MEM_KIND memKind
    ON e.memKind = memKind.id
LEFT JOIN
    ENUM_CUDA_DEV_MEM_EVENT_OPER memOper
    ON e.memoryOperationType = memOper.id
WHERE memKindName == "Device"
