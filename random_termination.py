from labeled_heap import LabeledHeap
import networkx as nx
import graph_utilities

def rt_double(graph, cost1, cost2, p, edgelist=False):
	node_incoming_neighbor_sets = { node: set(graph.predecessors(node)) for node in graph.nodes() }
	
	multicosts = { node: [cost1[node], cost2[node]] for node in graph.nodes() }
	local_minima = graph_utilities.find_local_minima(graph, multicosts, multiple_costs=True)
	far_nodes = set(filter(lambda node: node not in local_minima, graph.nodes()))
	considered_nodes = set(local_minima)
	accepted_nodes = set()
	expected_cost = { lm: [cost1[lm], cost2[lm]] for lm in local_minima }
	next_node = { lm:None for lm in local_minima }
	edgelist = []
	stationary_node_list = []

	compare_cost = lambda a,b: expected_cost[a] < expected_cost[b]
	heap = LabeledHeap(local_minima, is_less_than=compare_cost)

	while heap:
		accepted_node = heap.pop()
		considered_nodes.remove(accepted_node)
		accepted_nodes.add(accepted_node)

		if next_node[accepted_node] != None:
			edgelist.append((accepted_node, next_node[accepted_node]))
		else:
			stationary_node_list.append(accepted_node)

		for successor_node in graph.successors(accepted_node):
			# since this node's value is fixed, the updates on any of its
			# succssors won't affect the value of this node
			node_incoming_neighbor_sets[successor_node].remove(accepted_node)

		# update the value function on any of the accepted node's predecessors
		for neighbor_node in node_incoming_neighbor_sets[accepted_node]:
			
			expected_cost_assuming_motion = [ p*costi[accepted_node] + (1-p)*expected_cost[accepted_node][i] if costi[accepted_node] != expected_cost[accepted_node][i] else costi[accepted_node] for i, costi in enumerate([cost1, cost2])]
			
			if neighbor_node in far_nodes:
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				far_nodes.remove(neighbor_node)
				considered_nodes.add(neighbor_node)
				heap.push(neighbor_node)
				next_node[neighbor_node] = accepted_node
			elif expected_cost_assuming_motion < expected_cost[neighbor_node]:
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				heap.reheap_from_decrease_at_item(neighbor_node)
				next_node[neighbor_node] = accepted_node

	return expected_cost, edgelist, stationary_node_list

def random_termination_single_cost_edgelist(graph, cost, p):
	node_incoming_neighbor_sets = { node: set(graph.predecessors(node)) for node in graph.nodes() }
	
	local_minima = graph_utilities.find_local_minima(graph, cost, multiple_costs=False)
	far_nodes = set(
		filter(lambda node: node not in local_minima, graph.nodes()))
	considered_nodes = set(local_minima)
	accepted_nodes = set()
	expected_cost = { lm: cost[lm] for lm in local_minima }
	next_node = { lm:None for lm in local_minima }
	edgelist = []

	compare_cost = lambda a,b: expected_cost[a] < expected_cost[b]
	heap = LabeledHeap(local_minima, is_less_than=compare_cost)


	while heap:
		accepted_node = heap.pop()
#		assert accepted_node in considered_nodes
		considered_nodes.remove(accepted_node)
		accepted_nodes.add(accepted_node)
#		print(".")
#		print("\n\nAccepted node: %10s\tHeap: %d nodes" % (str(accepted_node), len(heap.heap)))
		if next_node[accepted_node] != None:
			edgelist.append((accepted_node, next_node[accepted_node]))

		for successor_node in graph.successors(accepted_node):
#			print(predecessor_node)
			assert successor_node in node_incoming_neighbor_sets.keys()
#			print(node_outgoing_neighbor_sets[predecessor_node])
			node_incoming_neighbor_sets[successor_node].remove(accepted_node)

		for neighbor_node in node_incoming_neighbor_sets[accepted_node]:
#			assert neighbor_node not in accepted_nodes
			
			expected_cost_assuming_motion = p*cost[accepted_node] + (1-p)*expected_cost[accepted_node] if cost[accepted_node] != expected_cost[accepted_node] else cost[accepted_node]

#			print("")
#			print(sorted(heap.item_index_dict.values()))
			if neighbor_node in far_nodes:
#				print("Adding node %s with value %3.1f" % (str(neighbor_node), expected_cost_assuming_motion))
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				far_nodes.remove(neighbor_node)
				considered_nodes.add(neighbor_node)
				heap.push(neighbor_node)
				heap.verify_dict()
				next_node[neighbor_node] = accepted_node
			elif expected_cost_assuming_motion < expected_cost[neighbor_node]:
#				print("Node %s value updated to %3.1f from %3.1f" % (str(neighbor_node), expected_cost_assuming_motion, expected_cost[neighbor_node]))
				assert neighbor_node in considered_nodes
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				heap.verify_dict()
				heap.reheap_from_decrease_at_item(neighbor_node)
				next_node[neighbor_node] = accepted_node
#			else:
#				print("No improvement on node %s" % (str(neighbor_node)))

#			print(sorted(heap.item_index_dict.values()))
	return expected_cost, edgelist



def random_termination_single_cost_edgelist_continuous_call_probability(graph, cost, p_call_per_unit_time):
	node_incoming_neighbor_sets = { node: set(graph.predecessors(node)) for node in graph.nodes() }
	
	local_minima = graph_utilities.find_local_minima(graph, cost, multiple_costs=False)
	far_nodes = set(
		filter(lambda node: node not in local_minima, graph.nodes()))
	considered_nodes = set(local_minima)
	accepted_nodes = set()
	expected_cost = { lm: cost[lm] for lm in local_minima }
	next_node = { lm:None for lm in local_minima }
	edgelist = []

	compare_cost = lambda a,b: expected_cost[a] < expected_cost[b]
	heap = LabeledHeap(local_minima, is_less_than=compare_cost)


	while heap:
		accepted_node = heap.pop()
#		assert accepted_node in considered_nodes
		considered_nodes.remove(accepted_node)
		accepted_nodes.add(accepted_node)
#		print(".")
#		print("\n\nAccepted node: %10s\tHeap: %d nodes" % (str(accepted_node), len(heap.heap)))
		if next_node[accepted_node] != None:
			edgelist.append((accepted_node, next_node[accepted_node]))

		for successor_node in graph.successors(accepted_node):
#			print(predecessor_node)
			assert successor_node in node_incoming_neighbor_sets.keys()
#			print(node_outgoing_neighbor_sets[predecessor_node])
			node_incoming_neighbor_sets[successor_node].remove(accepted_node)

		for neighbor_node in node_incoming_neighbor_sets[accepted_node]:
#			assert neighbor_node not in accepted_nodes
			
			p = p_call_per_unit_time*graph[neighbor_node][accepted_node]['weight']	
			expected_cost_assuming_motion = p*cost[accepted_node] + (1-p)*expected_cost[accepted_node] if cost[accepted_node] != expected_cost[accepted_node] else cost[accepted_node]

#			print("")
#			print(sorted(heap.item_index_dict.values()))
			if neighbor_node in far_nodes:
#				print("Adding node %s with value %3.1f" % (str(neighbor_node), expected_cost_assuming_motion))
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				far_nodes.remove(neighbor_node)
				considered_nodes.add(neighbor_node)
				heap.push(neighbor_node)
				heap.verify_dict()
				next_node[neighbor_node] = accepted_node
			elif expected_cost_assuming_motion < expected_cost[neighbor_node]:
#				print("Node %s value updated to %3.1f from %3.1f" % (str(neighbor_node), expected_cost_assuming_motion, expected_cost[neighbor_node]))
				assert neighbor_node in considered_nodes
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				heap.verify_dict()
				heap.reheap_from_decrease_at_item(neighbor_node)
				next_node[neighbor_node] = accepted_node
#			else:
#				print("No improvement on node %s" % (str(neighbor_node)))

#			print(sorted(heap.item_index_dict.values()))
	return expected_cost, edgelist

def random_termination_double_cost_edgelist(graph, cost, cost2, p):
	node_incoming_neighbor_sets = { node: set(graph.predecessors(node)) for node in graph.nodes() }
	double_cost = {node:[cost[node], cost2[node]] for node in cost.keys()} 
	
	local_minima = graph_utilities.find_local_minima(graph, double_cost, multiple_costs=False)
	far_nodes = set(
		filter(lambda node: node not in local_minima, graph.nodes()))
	considered_nodes = set(local_minima)
	accepted_nodes = set()
	expected_cost = { lm: double_cost[lm] for lm in local_minima }
	next_node = { lm:None for lm in local_minima }
	edgelist = []

	compare_cost = lambda a,b: expected_cost[a] < expected_cost[b]
	heap = LabeledHeap(local_minima, is_less_than=compare_cost)


	while heap:
		accepted_node = heap.pop()
#		assert accepted_node in considered_nodes
		considered_nodes.remove(accepted_node)
		accepted_nodes.add(accepted_node)
#		print(".")
#		print("\n\nAccepted node: %10s\tHeap: %d nodes" % (str(accepted_node), len(heap.heap)))
		if next_node[accepted_node] != None:
			edgelist.append((accepted_node, next_node[accepted_node]))

		for successor_node in graph.successors(accepted_node):
#			print(predecessor_node)
			assert successor_node in node_incoming_neighbor_sets.keys()
#			print(node_outgoing_neighbor_sets[predecessor_node])
			node_incoming_neighbor_sets[successor_node].remove(accepted_node)

		for neighbor_node in node_incoming_neighbor_sets[accepted_node]:
#			assert neighbor_node not in accepted_nodes
		
			if [cost[accepted_node], cost2[accepted_node]] != expected_cost[accepted_node]:
				expected_cost_assuming_motion = [p*cost[accepted_node] + (1-p)*expected_cost[accepted_node][0], p*cost2[accepted_node] + (1-p)*expected_cost[accepted_node][1]]
			else:
				expected_cost_assuming_motion = expected_cost[accepted_node]

#			print("")
#			print(sorted(heap.item_index_dict.values()))
			if neighbor_node in far_nodes:
#				print("Adding node %s with value %3.1f" % (str(neighbor_node), expected_cost_assuming_motion))
				expected_cost[neighbor_node] = expected_cost_assuming_motion
				far_nodes.remove(neighbor_node)
				considered_nodes.add(neighbor_node)
				heap.push(neighbor_node)
#				heap.verify_dict()
				next_node[neighbor_node] = accepted_node
			elif expected_cost_assuming_motion < expected_cost[neighbor_node]:
#				print("Node %s value updated to %3.1f from %3.1f" % (str(neighbor_node), expected_cost_assuming_motion, expected_cost[neighbor_node]))
				assert neighbor_node in considered_nodes
				expected_cost[neighbor_node] = expected_cost_assuming_motion
#				heap.verify_dict()
				heap.reheap_from_decrease_at_item(neighbor_node)
				next_node[neighbor_node] = accepted_node
#			else:
#				print("No improvement on node %s" % (str(neighbor_node)))

#			print(sorted(heap.item_index_dict.values()))
	return expected_cost, edgelist
