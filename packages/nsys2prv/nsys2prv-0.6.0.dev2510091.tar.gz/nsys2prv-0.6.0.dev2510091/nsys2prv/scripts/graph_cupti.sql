SELECT  
	gt.start,
	gt.end,
	(gt.globalPid / 0x1000000 % 0x1000000) as Pid,
	printf('%s (%d)', gpu.name, deviceId) AS "Device",
	deviceId as "deviceid",
	contextId AS "context",
	greenContextId AS "greenContext",
	streamId AS "Strm",
	correlationId as "CorrID",
	gt.graphId,
	gt.graphExecId,
	printf('Graph Exec %d', gt.graphExecId) as Name
FROM CUPTI_ACTIVITY_KIND_GRAPH_TRACE as gt
LEFT JOIN
	TARGET_INFO_GPU AS gpu
	ON gpu.id == gt.deviceId