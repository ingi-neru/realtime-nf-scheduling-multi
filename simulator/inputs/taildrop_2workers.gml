graph [
	name "Taildrop Chain"
	directed 1
	Q 1
	B 1
	resource_reallocation 1
	reallocation_strategies "all"
	num_workers 2
	node
	[
		id 1
		label 1
		pos 0
		pos 0
		task 0
		taskname "Task 0"
		worker 0
		workerspeed 1
		cost 1
		flows
		[
			flow
			[
				flowid 0
				flowname "Flow 0"
				flowrate 10
				flowrateSLO 0.06
				flowdelaySLO 50
			]
		]
	]
	node
	[
		id 2
		label 2
		pos 2
		pos 0
		task 1
		taskname "Task 1"
		worker 0
		workerspeed 1
		cost 1
		flows
		[
			flow
			[
				flowid 0
				flowname "Flow 0"
				flowrate 10
				flowrateSLO 0.06
				flowdelaySLO 35
			]
		]
	]
	node
	[
		id 3
		label 3
		pos 4
		pos 0
		task 2
		taskname "Task 2"
		worker 0
		workerspeed 1
		cost 10
		flows
		[
			flow
			[
				flowid 0
				flowname "Flow 0"
				flowrate 10
				flowrateSLO 0.06
				flowdelaySLO 35
			]
		]
	]
	edge [
		source 1
		target 2
	]
	edge [
		source 2
		target 3
	]
]
