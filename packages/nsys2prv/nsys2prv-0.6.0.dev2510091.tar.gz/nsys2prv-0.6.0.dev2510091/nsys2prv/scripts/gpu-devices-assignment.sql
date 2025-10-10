WITH ci as ( SELECT processId, nullStreamId, contextId, deviceId FROM TARGET_INFO_CUDA_CONTEXT_INFO )
SELECT ci.processId, ci.nullStreamId, ci.contextId, ci.deviceId, cd.gpuId, cd.cudaId, ig.busLocation, ig.name, ig.cuDevice
FROM ci
LEFT JOIN TARGET_INFO_CUDA_DEVICE as cd
ON (ci.processId == cd.pid AND ci.deviceId == cd.cudaId)
LEFT JOIN TARGET_INFO_GPU as ig
ON cd.gpuId == ig.id