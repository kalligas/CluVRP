import random


class Tsp:
    def __init__(self, solver):
        self.distance_matrix = solver.distance_matrix
        self.cluster_routes = solver.cluster_routes
        self.clusters = solver.clusters
        self.depot = solver.depot
        self.hard = solver.hard
        self.length_of_rcl = solver.length_of_rcl
        self.construction_method = solver.construction_method
        self.initial_solution = solver.initial_solution

    def initialize_tsp(self):
        """Finds for each cluster route the nearest node of the first cluster to the depot."""
        for cluster_route in self.cluster_routes:
            min_dist = 10 ** 9
            # Define the first cluster of the cluster route
            cluster = cluster_route.sequence_of_clusters[1]
            # Find nearest node to depot.
            for node in cluster.nodes:
                candidate = self.distance_matrix[self.depot.ID][node.ID]
                if candidate < min_dist:
                    min_dist = candidate
                    cluster_route.nearest_node = node

    def solve_randomly(self, nodes, current_route):
        # random solution
        not_routed = nodes.copy()
        while not_routed:
            inserted_customer = random.choice(not_routed)
            not_routed = [i for i in not_routed if i.ID != inserted_customer.ID]
            current_route.add(inserted_customer, self.distance_matrix)

    def find_neighbors(self, node, nodes_list):
        """
        Finds a number of the nearest neighbors of a node in a nodes-list.
        Input a length (self.length_of_rcl) bigger than 1 to activate the restricted candidate list mode.
        This mode helps to generate diverse initial solutions to explore a wider part of
        the solution space during the local search
        """
        for candidate in nodes_list:
            if node == candidate:
                continue
            if candidate.is_routed:
                continue
            cost = self.distance_matrix[node.ID][candidate.ID]
            if len(node.neighbors) < self.length_of_rcl:
                new_tup = (cost, candidate)
                node.neighbors.append(new_tup)
                node.neighbors.sort(key=lambda x: x[0])
            elif cost < node.neighbors[-1][0]:
                node.neighbors.pop(len(node.neighbors) - 1)
                new_tup = (cost, candidate)
                node.neighbors.append(new_tup)
                node.neighbors.sort(key=lambda x: x[0])

    def apply_nearest_neighbor(self, nodes, current_route):
        # nearest neighbor solution
        all_routed = all([node.is_routed for node in nodes])
        while not all_routed:
            last_routed_customer = current_route.sequence_of_nodes[-2]
            # the construction_method below  returns the list of candidate customers and finds the neighbors of
            # last_routed_customer in that list
            self.find_neighbors(last_routed_customer, nodes)
            inserted_customer = random.choice(last_routed_customer.neighbors)
            current_route.add(inserted_customer[1], self.distance_matrix)
            all_routed = all([node.is_routed for node in nodes])

    def apply_construction_method(self, node_list, current_route):
        """
        Applies one of three construction methods depending on the user's choice
        :param node_list: The nodes meant for routing
        :param current_route:  Route under construction
        """
        if self.construction_method == 1:
            self.solve_randomly(node_list, current_route)
        elif self.construction_method == 0:
            self.apply_nearest_neighbor(node_list, current_route)

    def construct_solution(self):
        """
        Constructs initial solution for hard clustered or soft clustered problems
        """

        # initialize the procedure by finding the nearest nodes to the depot from each first-in-cluster-route cluster
        self.initialize_tsp()

        for cluster_route in self.cluster_routes:

            # define current route
            current_route = cluster_route.node_route

            # initialize the node route by adding:

            # the depot in the start
            current_route.sequence_of_nodes.append(self.depot)
            # the nearest node
            current_route.sequence_of_nodes.append(cluster_route.nearest_node)
            current_route.cost += self.distance_matrix[cluster_route.nearest_node.ID][self.depot.ID]
            current_route.load += cluster_route.nearest_node.demand
            cluster_route.nearest_node.is_routed = True
            # the depot in the end
            current_route.sequence_of_nodes.append(self.depot)

            # the problem will be tackled differently if we define it as hard clustered or soft clustered
            if self.hard:
                # if hard, solve each cluster distinctly (as many open-type tsps as the clusters in the cluster route)

                for cluster in cluster_route.sequence_of_clusters:
                    # the cluster of the nearest node has already been serviced, so we must skip it
                    # we also skip the depot cluster
                    if cluster.ID == self.depot.cluster:
                        continue
                    # solve open-type tsp for the nodes of the cluster
                    self.apply_construction_method(cluster.nodes, current_route)
                last_customer = current_route.sequence_of_nodes[-2]
                current_route.cost += self.distance_matrix[last_customer.ID][self.depot.ID]

            else:
                # in case we tackle the problem as soft clustered, the whole cluster-route will be solved as
                # a closed-type tsp

                node_list = []
                for cluster in cluster_route.sequence_of_clusters:
                    # create a node list by merging the nodes of each cluster while ignoring the depot
                    if cluster.ID == self.depot.cluster:
                        continue
                    node_list += cluster.nodes
                    # solve the tsp instance
                self.apply_construction_method(node_list, current_route)
                last_customer = current_route.sequence_of_nodes[-2]
                current_route.cost += self.distance_matrix[last_customer.ID][self.depot.ID]

            self.initial_solution.routes.append(cluster_route.node_route.sequence_of_nodes)
            self.initial_solution.cost_per_route.append(cluster_route.node_route.cost)
            self.initial_solution.total_cost += cluster_route.node_route.cost
        return self.initial_solution
