
graph [
 	name "Example MultiSwitch Configuration"
	resource_reallocation 1
	reallocation_strategies "least_constrained"
  endtoend_controller 1
 	directed 1
  num_workers 2
 	Q 1
 	B 1
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
		cost 0
    switch 0
		flows
		[
        		flow
        		[
          			flowid 0
				flowname "Flow 0"
          			flowrate 10
          			flowrateSLO 0.4
          			flowdelaySLO 5
        		]
        		flow
          [
            flowid 1
            flowname "Flow 1"
            flowrate 12
            flowrateSLO 0.1
            flowdelaySLO 11
          ]
    ]
	]
	node
	[
		id 2
		label 2
		pos 2
		pos 0
		task 0
		taskname "Task 0"
		worker 0
		workerspeed 1
		cost 0
    switch 0
		flows
		[
        		flow
        		[
          			flowid 0
				flowname "Flow 0"
          			flowrate 10
          			flowrateSLO 0.4
          			flowdelaySLO 5
        		]
        		flow
			[
				flowid 1
				flowname "Flow 1"
				flowrate 12
				flowrateSLO 0.1
				flowdelaySLO 11
			]
        	]
	]
	node
	[
		id 3
		label 3
		pos 4
		pos 2
		task 1
		taskname "Task 1"
		worker 0
		workerspeed 1
		cost 1
    switch 0
		flows
		[
        		flow
        		[
          			flowid 0
				flowname "Flow 0"
          			flowrate 10
          			flowrateSLO 0.4
          			flowdelaySLO 5
        		]
        	]
	]
	node
	[
		id 4
		label 4
		pos 0
		pos 0
		task 2
		taskname "Task 2"
		worker 0
		workerspeed 1
		cost 1
    switch 0
		flows
		[
        		flow
			[
				flowid 1
				flowname "Flow 1"
				flowrate 12
				flowrateSLO 0.1
				flowdelaySLO 11
			]
        	]
	]
	node
	[
		id 5 
		label 5 
		pos 4
		pos 2
		task 3
		taskname "Task 3"
		worker 0
		workerspeed 1
		cost 1
    switch 1
		flows
		[
        		flow
        		[
          			flowid 0
				flowname "Flow 0"
          			flowrate 10
          			flowrateSLO 0.4
          			flowdelaySLO 5
        		]
        	]
	]
	node
	[
		id 6
		label 6
		pos 0
		pos 0
		task 4 
		taskname "Task 4"
		worker 0
		workerspeed 1
		cost 1
    switch 1
		flows
		[
        		flow
			[
				flowid 1
				flowname "Flow 1"
				flowrate 12
				flowrateSLO 0.1
				flowdelaySLO 11
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
  edge [
    source 2
    target 4
  ]
  edge [
    source 3
    target 5
  ]
  edge [
    source 4
    target 6
    ]  
]
