from collections import defaultdict
import numpy as np
import networkx as nx
import json

def grid_graph(n_columns, n_rows):

	graph = nx.DiGraph()
	s2 = 1.4142135623730951

	for i_rows in xrange(n_rows):
		for i_columns in xrange(n_columns):

			graph.add_node((i_columns, i_rows), pos=(i_columns, i_rows))

			if i_rows != 0:
				graph.add_edge((i_columns, i_rows), (i_columns, i_rows-1), weight=1)
				graph.add_edge((i_columns, i_rows-1), (i_columns, i_rows), weight=1)

			if i_rows != 0 and i_columns != 0:
				graph.add_edge((i_columns, i_rows), (i_columns-1, i_rows-1), weight=s2)
				graph.add_edge((i_columns-1, i_rows-1), (i_columns, i_rows), weight=s2)

			if i_columns != 0: 
				graph.add_edge((i_columns, i_rows), (i_columns-1, i_rows), weight=1)
				graph.add_edge((i_columns-1, i_rows), (i_columns, i_rows), weight=1)

			if i_columns != (n_columns-1) and i_rows != 0:
				graph.add_edge((i_columns, i_rows), (i_columns+1, i_rows-1), weight=s2)
				graph.add_edge((i_columns+1, i_rows-1), (i_columns, i_rows), weight=s2)
	return graph	

def distances_by_location(graph, caller_locations):
	""" graph is a networkx graph
      caller_locations is a list of nodes within the graph
		
			distances_by_location(graph, caller_locations) produces a 
				dictionary, keyed by node, which returns a list of the
				minimum distance to each caller location.
			If d is the minimum distance between node_a and node_b, and
				caller_locations[i] = node_a, then:

			distances_by_location(graph, caller_locations)[node_b][i] = node_a

			Internally, distances_by_location uses networkx's function
				netowrkx.algorithms.single_source_dijkstra_path_length """

	# make sure tha caller_locations is a list
	assert type(caller_locations) is list, "caller_locations must be a list"

	# initialize an empty dictionary, with an empty list as the default value
	distances_by_location = defaultdict(list)

	for caller_location in caller_locations:
		# using dijkstra's algorithm on graph, build up a dictionary of distances
		distances_from_caller_location = nx.algorithms.single_source_dijkstra_path_length(graph, caller_location)

		for node in graph.nodes():
			# put the distance from caller_locations[i] to node in the ith index of
			#    the list corresponding to node.
			distances_by_location[node] += [distances_from_caller_location[node]]

	return distances_by_location

# TODO better name
def graph_cost(graph, caller_locations, caller_relative_probabilities, cost_function):
	"""
		graph is a networkx graph
		caller_locations is a list of nodes contained within the graph from 
			calls can originate
		caller_relative_probabilities is a list of the probability that, given a call,
			the call comes from each node

		RETURNS
		a dict of nodes paired with their costs, calculated by the cost_function.

		cost_function(node, caller_relative_probabilities, caller_distances) is
			a function which assigns a terminal cost to each node, based on the
			distance from that node to the caller nodes, and the probability that
			each caller node is the one which is active.

		An example cost function assigns the expected distance as the cost:

		def expected_value_cost(_, caller_relative_probabilities,  caller_distances):
			return np.dot(caller_relative_probabilities, caller_distances)

		Another example cost function assigns the probability of a threshold
			distance being exceeded by a call as the cost function:

		def probability_of_exceeding_allowed_distance_cost(node, caller_relative_probabilities, caller_distances):
			return np.sum( caller_relative_probablities[ caller_distances > threshold distance ])

	"""

	distances_to_callers = distances_by_location(graph, caller_locations)

	return { node: cost_function(node, caller_relative_probabilities, 
							np.array(distances_to_callers[node]))
						for node in graph.nodes() }

def expected_value(node, caller_relative_probabilities, caller_distances):
	""" Calculates the expected distance of a call """
	return np.dot(caller_relative_probabilities, caller_distances)

def make_exceeding_distance_cost(allowed_distance):
	""" returns a FUNCTION which calculates the probability that the
		caller distances in a node will exceed the allowed distance.
	"""
	def exceeding_distance_cost(node, caller_relative_probabilities, caller_distances):
		return np.sum(caller_relative_probabilities[caller_distances > allowed_distance])

	return exceeding_distance_cost

def find_local_minima(graph, cost, multiple_costs=False):
	local_minima = []

	if not multiple_costs:
		for node in graph.nodes():
			if cost[node] <= min([ cost[nn] for nn in graph.successors(node)]):
				local_minima.append(node)
	else:
		for node in graph.nodes():
			for i in xrange(len(cost[node])):
				if cost[node][i] <= min([cost[nn][i] for nn in graph.successors(node)]):
					if cost[node][i] < min([cost[nn][i] for nn in graph.successors(node)]):
						local_minima.append(node)
						break
					else:
						if len(cost[node])-1 == i:
							local_minima.append(node)
							break
				else:
					break	
	return local_minima

def sf_map():
	network_file = open("SF network.json")
	roads = []
	for line in network_file:
		roads += [json.loads(line)]
	network_file.close()

	n = len(roads)
	roads_starting_at_node = defaultdict(list)
	roads_ending_at_node = defaultdict(list)

	g = nx.DiGraph()
	for i in xrange(n):
		g.add_edge(
			roads[i]['startNodeId']['primary'], 
			roads[i]['endNodeId']['primary'],
			roads[i],
			weight=roads[i]['length']/roads[i]['speedLimit'])

		roads_starting_at_node[roads[i]['startNodeId']['primary']].append((roads[i]['id']['primary'], roads[i]['id']['secondary'], i))
		roads_ending_at_node[roads[i]['endNodeId']['primary']].append((roads[i]['id']['primary'], roads[i]['id']['secondary'], i))

	node_coordinates = {}
	for node in g.nodes():
		s1 = map(lambda a: (a[2], 0), roads_starting_at_node[node])
		s2 = map(lambda a: (a[2], -1), roads_ending_at_node[node])
		position_data_dicts = [ roads[road_index]['geom']['points'][point_index] for road_index, point_index in s1+s2 ]
		position_data = np.array(map(lambda a: [a['lon'],a['lat']], position_data_dicts))
		mean_lon, mean_lat = np.mean(position_data, axis=0)
		node_coordinates[node] = (mean_lon, mean_lat)
	nx.set_node_attributes(g, 'pos', node_coordinates)
	return g

def make_direction_subgraph(graph, edgelist):
	g = nx.DiGraph()
	for node in graph.nodes():
		g.add_node(node)
	for edge in edgelist:
		g.add_edge(*edge)
	return g

def make_path(direction_subgraph, start_node):
	path = [start_node]
	while direction_subgraph.neighbors(path[-1]):
		path.append(direction_subgraph.neighbors(path[-1])[0])
	return path

def make_path_edgelist(path):
	path_edgelist = []
	for i in xrange(len(path)-1):
		path_edgelist.append((path[i], path[i+1]))
	return path_edgelist

def summed_pdf(graph, path, caller_locations,
	caller_relative_probabilities, p):
	
	distances = distances_by_location(graph, caller_locations)
	pdf = defaultdict(float)
	n = len(path)

	if n <= 2:
		for distance, prob in zip(distances[path[-1]], caller_relative_probabilities):
			pdf[distance] += prob

	else:
		ending_probabilities = [ p*(1-p)**(i-1) for i in xrange(len(path)) ]
		ending_probabilities[0] = 0.0
		ending_probabilities[-1] = (1-p)**(len(path)-2)
	
		for reaching_prop, path_node in zip(ending_probabilities, path):
			for distance, probability, caller in zip(distances[path_node], caller_relative_probabilities, caller_locations):
				pdf[distance] += reaching_prop*probability
	return pdf		

def make_pdf(pdf_dict):
	p = np.array(pdf_dict.values())
	d = np.array(pdf_dict.keys())
	ordering = np.argsort(d)
	return d[ordering], p[ordering]

def make_cdf(pdf_dict):
	d,p = make_pdf(pdf_dict)
	p_cum = np.cumsum(p)
	return d, p_cum

def step_pts(x, y):
	x_ = np.empty(2*len(x) - 1)
	y_ = np.empty(2*len(x) - 1)
	x_[::2] = x
	x_[1::2] = x[1:]
	y_[::2] = y
	y_[1::2] = y[:-1]
	return x_, y_

def plot_graph(graph, node_values, minscale, maxscale, edgelist, node_groups, coloring_group_index=0, figsize=(13,13)):

    """plot_sf(central_sf, sf_cost_expectation, 0, 600.0, central_sf.edges(), 
        [(central_sf_caller_locations, {"node_size":300}), 
         (not_caller, {"node_size":15})])"""
    
    for i, (node_group, node_options) in enumerate(node_groups):
        
        am = nx.draw_networkx_nodes(
            graph,
            pos=nx.get_node_attributes(graph, 'pos'),
            node_color=[node_values[n] for n in node_group],
            with_labels=False,
            nodelist=node_group,
            vmin=minscale,
            vmax=maxscale,
            **node_options)
        
        if i == coloring_group_index:
            ami = am
        
    nx.draw_networkx_edges(
        graph,
        edgelist=edgelist,
        pos=nx.get_node_attributes(graph, 'pos'),
        arrows=True,
        edge_color="grey")
    
    return ami
