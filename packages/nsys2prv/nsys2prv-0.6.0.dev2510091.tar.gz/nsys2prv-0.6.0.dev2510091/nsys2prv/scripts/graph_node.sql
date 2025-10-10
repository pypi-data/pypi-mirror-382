SELECT  
	ge.start,
	ge.end,
	et.label as eventClass,
	(ge.globalTid / 0x1000000 % 0x1000000) as Pid,
	(ge.globalTid % 0x1000000) as Tid,
	sid.value as name,
	ge.graphNodeId
FROM CUDA_GRAPH_NODE_EVENTS as ge
	LEFT JOIN
	ENUM_NSYS_EVENT_CLASS as et
	ON ge.eventClass = et.id
	LEFT OUTER JOIN
		StringIds as sid
		ON ge.nameId = sid.id