graph [
	name "MobileGateWay"
	directed 1
	Q 1
	B 1
	node [
		id 0
		label 0
		name "mac_table"
		cost 0.018908338662412205
		task 0
		taskname "ingress"
		worker 0
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 1
		label 1
		name "type_check"
		cost 0.16219187323610268
		task 0
		taskname "ingress"
		worker 0
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 2
		label 2
		name "dir_selector"
		cost 0.2663162575270169
		task 0
		taskname "ingress"
		worker 0
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 3
		label 3
		name "dl_br_selector"
		cost 0.6065695060485391
		task 0
		taskname "egress"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 4
		label 4
		name "vxlan_decap"
		cost 0.3957608178097989
		task 0
		taskname "ingress"
		worker 0
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 5
		label 5
		name "ul_br_selector"
		cost 0.508744625805023
		task 0
		taskname "egress"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 6
		label 6
		name "update_ttl"
		cost 0.44531217307352683
		task 0
		taskname "egress"
		worker 2
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 7
		label 7
		name "L3"
		cost 0.005311394635696798
		task 0
		taskname "egress"
		worker 2
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 8
		label 8
		name "update_mac_dl"
		cost 0.053473032843182056
		task 0
		taskname "egress"
		worker 2
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 9
		label 9
		name "ip_checksum_dl"
		cost 0.18863563577573067
		task 0
		taskname "egress"
		worker 2
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 10
		label 10
		name "update_mac_ul"
		cost 0.4203806793998657
		task 0
		taskname "egress"
		worker 2
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 11
		label 11
		name "ip_checksum_ul"
		cost 0.39640481445825704
		task 0
		taskname "egress"
		worker 2
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 12
		label 12
		name "dl_ue_selector_0"
		cost 0.2550858294277841
		task 0
		taskname "ingress"
		worker 0
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 13
		label 13
		name "ul_ue_selector_0"
		cost 0.34874224589953806
		task 0
		taskname "ingress"
		worker 0
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 14
		label 14
		name "ul_user_bp_0_0"
		cost 0.8606265901908243
		task 3
		taskname "bearer0_ul_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 15
		label 15
		name "setmd_ul_0_0"
		cost 0.7121947156364141
		task 3
		taskname "bearer0_ul_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 0
				flowname "user0_ul_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 16
		label 16
		name "dl_user_bp_0_0"
		cost 0.8781775201622647
		task 0
		taskname "bearer0_dl_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 17
		label 17
		name "setmd_dl_0_0"
		cost 0.33709856491848655
		task 0
		taskname "bearer0_dl_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 18
		label 18
		name "vxlan_encap_0_0"
		cost 0.5461733746093309
		task 0
		taskname "bearer0_dl_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 19
		label 19
		name "ip_encap_0_0"
		cost 0.8790388289697241
		task 0
		taskname "bearer0_dl_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 20
		label 20
		name "ether_encap_0_0"
		cost 0.12711419382834754
		task 0
		taskname "bearer0_dl_user0"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 1
				flowname "user0_dl_qos"
				flowrate 3
				flowrateSLO 2
				flowdelaySLO 0.45
			]
		]
	]
	node [
		id 21
		label 21
		name "dl_ue_selector_1"
		cost 0.2550858294277841
		task 2
		taskname "bearer_dl_1"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 22
		label 22
		name "ul_ue_selector_1"
		cost 0.34874224589953806
		task 5
		taskname "bearer_ul_1"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 23
		label 23
		name "ul_user_bp_0_1"
		cost 0.8606265901908243
		task 5
		taskname "bearer1_ul"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 24
		label 24
		name "setmd_ul_0_1"
		cost 0.7121947156364141
		task 5
		taskname "bearer1_ul"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 2
				flowname "user0_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 25
		label 25
		name "dl_user_bp_0_1"
		cost 0.8781775201622647
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 26
		label 26
		name "setmd_dl_0_1"
		cost 0.33709856491848655
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 27
		label 27
		name "vxlan_encap_0_1"
		cost 0.5461733746093309
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 28
		label 28
		name "ip_encap_0_1"
		cost 0.8790388289697241
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 29
		label 29
		name "ether_encap_0_1"
		cost 0.12711419382834754
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 3
				flowname "user0_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 30
		label 30
		name "ul_user_bp_1_1"
		cost 0.8606265901908243
		task 5
		taskname "bearer1_ul"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 31
		label 31
		name "setmd_ul_1_1"
		cost 0.7121947156364141
		task 5
		taskname "bearer1_ul"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 4
				flowname "user1_ul_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 32
		label 32
		name "dl_user_bp_1_1"
		cost 0.8781775201622647
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 33
		label 33
		name "setmd_dl_1_1"
		cost 0.33709856491848655
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 34
		label 34
		name "vxlan_encap_1_1"
		cost 0.5461733746093309
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 35
		label 35
		name "ip_encap_1_1"
		cost 0.8790388289697241
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	node [
		id 36
		label 36
		name "ether_encap_1_1"
		cost 0.12711419382834754
		task 2
		taskname "bearer1_dl"
		worker 1
		workerspeed 60
		flows
		[
			flow
			[
				flowid 5
				flowname "user1_dl_bulk1"
				flowrate 8
				flowrateSLO 0.1
				flowdelaySLO 0.75
			]
		]
	]
	edge [
		source 26
		target 27
	]
	edge [
		source 12
		target 16
	]
	edge [
		source 35
		target 36
	]
	edge [
		source 5
		target 13
	]
	edge [
		source 22
		target 23
	]
	edge [
		source 21
		target 25
	]
	edge [
		source 8
		target 9
	]
	edge [
		source 17
		target 18
	]
	edge [
		source 5
		target 22
	]
	edge [
		source 27
		target 28
	]
	edge [
		source 25
		target 26
	]
	edge [
		source 13
		target 14
	]
	edge [
		source 7
		target 10
	]
	edge [
		source 32
		target 33
	]
	edge [
		source 18
		target 19
	]
	edge [
		source 36
		target 6
	]
	edge [
		source 4
		target 5
	]
	edge [
		source 3
		target 12
	]
	edge [
		source 14
		target 15
	]
	edge [
		source 23
		target 24
	]
	edge [
		source 3
		target 21
	]
	edge [
		source 0
		target 1
	]
	edge [
		source 2
		target 4
	]
	edge [
		source 1
		target 2
	]
	edge [
		source 10
		target 11
	]
	edge [
		source 19
		target 20
	]
	edge [
		source 28
		target 29
	]
	edge [
		source 29
		target 6
	]
	edge [
		source 6
		target 7
	]
	edge [
		source 20
		target 6
	]
	edge [
		source 31
		target 6
	]
	edge [
		source 33
		target 34
	]
	edge [
		source 22
		target 30
	]
	edge [
		source 21
		target 32
	]
	edge [
		source 34
		target 35
	]
	edge [
		source 24
		target 6
	]
	edge [
		source 2
		target 3
	]
	edge [
		source 15
		target 6
	]
	edge [
		source 7
		target 8
	]
	edge [
		source 30
		target 31
	]
	edge [
		source 16
		target 17
	]
]