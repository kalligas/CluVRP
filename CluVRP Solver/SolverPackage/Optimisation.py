import random


class RelocationMove(object):
    def __init__(self):
        self.original_position = None
        self.new_position = None
        self.cost = None

    def initialize(self):
        self.cost = 10 ** 9
        self.original_position = None
        self.new_position = None


class SwapMove(object):
    def __init__(self):
        self.first = None
        self.second = None
        self.cost = None

    def initialize(self):
        self.cost = 10 ** 9
        self.first = None
        self.second = None


class TwoOptMove(object):
    def __init__(self):
        self.first = None
        self.second = None
        self.cost = None

    def initialize(self):
        self.cost = 10 ** 9
        self.first = None
        self.second = None


class Optimisation:
    def __init__(self, solver):
        self.distance_matrix = solver.distance_matrix
        self.depot = solver.depot
        self.hard = solver.hard
        self.move_type = solver.move_type
        self.optimisation_method = solver.optimisation_method
        self.best_cost = None
        self.updated_cost = None

    def create_subroutes(self, sequence_of_nodes):
        """
        Takes a node-route that may contain nodes from different clusters and splits it into subroutes for each distinct
        cluster. We do that to optimise each cluster distinctly.
        """
        subroutes = []
        current_subroute = 0
        for current_node, _ in enumerate(sequence_of_nodes):
            # If the subroutes list is empty, create a new subroute and add the first node (depot).
            if not subroutes:
                subroutes.append([])
                subroutes[current_subroute].append(sequence_of_nodes[current_node])
            # Else if the previous node belongs to a different cluster (depot cluster or other node cluster) add the
            # current node to the subroute. We do that for two reasons:
            # 1) because the previous node may be the depot.
            # 2) the current node may be the depot.
            # 3) we also want to optimise the transition from current cluster to the next one. For that to happen, each
            #    subroute must contain in its last position the first node of the next cluster.
            elif sequence_of_nodes[current_node - 1].cluster != sequence_of_nodes[current_node].cluster:
                subroutes[current_subroute].append(sequence_of_nodes[current_node])
            # Else if the (node != depot) BEFORE the PREVIOUS node belongs to a different cluster, create a new subroute
            # and add the current node.
            elif sequence_of_nodes[current_node - 2].cluster != sequence_of_nodes[current_node].cluster \
                    and sequence_of_nodes[current_node - 2].cluster != self.depot.cluster:
                current_subroute += 1
                subroutes.append([])
                subroutes[current_subroute].append(sequence_of_nodes[current_node])
            # Else, the current node will belong to the same cluster as the previous one, so it should be added to the
            # subroute.
            else:
                subroutes[current_subroute].append(sequence_of_nodes[current_node])
        return subroutes

    def calculate_route_cost(self, sequence_of_nodes):
        cost = 0
        for current_position, node in enumerate(sequence_of_nodes):
            if current_position != 0:
                node_a = sequence_of_nodes[current_position - 1]
                node_b = sequence_of_nodes[current_position]
                cost += self.distance_matrix[node_a.ID][node_b.ID]
        return cost

    def find_best_relocation_move(self, sequence_of_nodes, rm):

        for current_position in range(1, len(sequence_of_nodes) - 1):

            node_a = sequence_of_nodes[current_position - 1]
            node_b = sequence_of_nodes[current_position]
            node_c = sequence_of_nodes[current_position + 1]

            for current_relocated_position in range(0, len(sequence_of_nodes) - 1):

                # do not relocate to the same position
                if current_relocated_position != current_position \
                        and current_relocated_position != current_position - 1:

                    node_f = sequence_of_nodes[current_relocated_position]
                    node_g = sequence_of_nodes[current_relocated_position + 1]

                    costs_removed = self.distance_matrix[node_a.ID][node_b.ID] + \
                                    self.distance_matrix[node_f.ID][node_g.ID] + \
                                    self.distance_matrix[node_b.ID][node_c.ID]

                    costs_added = self.distance_matrix[node_f.ID][node_b.ID] + \
                                  self.distance_matrix[node_b.ID][node_g.ID] + \
                                  self.distance_matrix[node_a.ID][node_c.ID]

                    cost = costs_added - costs_removed

                    if cost < rm.cost:
                        rm.cost = cost
                        rm.original_position = current_position
                        rm.new_position = current_relocated_position

    def find_best_swap_move(self, sequence_of_nodes, sm):
        for position_1 in range(1, len(sequence_of_nodes) - 1):

            node_a = sequence_of_nodes[position_1 - 1]
            node_b = sequence_of_nodes[position_1]
            node_c = sequence_of_nodes[position_1 + 1]

            for position_2 in range(position_1 + 1, len(sequence_of_nodes) - 1):

                node_d = sequence_of_nodes[position_2 - 1]
                node_e = sequence_of_nodes[position_2]
                node_f = sequence_of_nodes[position_2 + 1]

                if position_2 == position_1 + 1:
                    costs_removed = self.distance_matrix[node_a.ID][node_b.ID] + \
                                    self.distance_matrix[node_b.ID][node_c.ID] + \
                                    self.distance_matrix[node_c.ID][node_f.ID]

                    costs_added = self.distance_matrix[node_a.ID][node_c.ID] + \
                                  self.distance_matrix[node_c.ID][node_b.ID] + \
                                  self.distance_matrix[node_b.ID][node_f.ID]

                else:
                    costs_removed = self.distance_matrix[node_a.ID][node_b.ID] + \
                                    self.distance_matrix[node_b.ID][node_c.ID] + \
                                    self.distance_matrix[node_d.ID][node_e.ID] + \
                                    self.distance_matrix[node_e.ID][node_f.ID]

                    costs_added = self.distance_matrix[node_a.ID][node_e.ID] + \
                                  self.distance_matrix[node_e.ID][node_c.ID] + \
                                  self.distance_matrix[node_d.ID][node_b.ID] + \
                                  self.distance_matrix[node_b.ID][node_f.ID]

                cost = costs_added - costs_removed

                if cost < sm.cost:
                    sm.cost = cost
                    sm.first = position_1
                    sm.second = position_2

    def find_best_two_opt_move(self, sequence_of_nodes, top):
        for position_1 in range(0, len(sequence_of_nodes) - 1):
            node_a = sequence_of_nodes[position_1]
            node_b = sequence_of_nodes[position_1 + 1]

            for position_2 in range(position_1 + 2, len(sequence_of_nodes) - 1):

                node_k = sequence_of_nodes[position_2]
                node_l = sequence_of_nodes[position_2 + 1]

                costs_added = self.distance_matrix[node_a.ID][node_k.ID] + self.distance_matrix[node_b.ID][node_l.ID]
                costs_removed = self.distance_matrix[node_a.ID][node_b.ID] + self.distance_matrix[node_k.ID][node_l.ID]

                cost = costs_added - costs_removed

                if cost < top.cost:
                    top.cost = cost
                    top.first = position_1 + 1
                    top.second = position_2

    @staticmethod
    def apply_relocation_move(sequence_of_nodes, rm):
        node = sequence_of_nodes[rm.original_position]
        del sequence_of_nodes[rm.original_position]

        if rm.new_position < rm.original_position:
            sequence_of_nodes.insert(rm.new_position + 1, node)
        else:
            sequence_of_nodes.insert(rm.new_position, node)

    @staticmethod
    def apply_swap_move(sequence_of_nodes, sm):
        node_a = sequence_of_nodes[sm.first]
        node_b = sequence_of_nodes[sm.second]
        sequence_of_nodes[sm.first] = node_b
        sequence_of_nodes[sm.second] = node_a

    @staticmethod
    def apply_two_opt_move(sequence_of_nodes, top):
        # top.second + 1 because the list indexing stops at -1
        sequence_of_nodes[top.first: top.second + 1] = sequence_of_nodes[top.first: top.second + 1][::-1]

    def local_search(self, sequence_of_nodes):
        best_sequence = sequence_of_nodes[:]
        best_cost = self.calculate_route_cost(best_sequence)
        termination_condition = False
        if len(best_sequence) < 4:
            return best_sequence, best_cost

        iterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        while termination_condition is False:
            rm.initialize()
            sm.initialize()
            top.initialize()
            # SolDrawer.draw(iterator, self.solution, self.allNodes)
            # Relocations
            if self.move_type == 0:
                self.find_best_relocation_move(best_sequence, rm)
                if rm.original_position is not None:
                    if rm.cost < -0.00001:
                        self.apply_relocation_move(best_sequence, rm)
                        best_cost = best_cost + rm.cost
                    else:
                        termination_condition = True
                else:
                    termination_condition = True
            # Swaps
            elif self.move_type == 1:
                self.find_best_swap_move(best_sequence, sm)
                if sm.first is not None:
                    if sm.cost < -0.00001:
                        self.apply_swap_move(best_sequence, sm)
                        best_cost = best_cost + sm.cost
                    else:
                        termination_condition = True
                else:
                    termination_condition = True

            # TwoOpt
            elif self.move_type == 2:
                self.find_best_two_opt_move(best_sequence, top)
                if top.first is not None:
                    if top.cost < -0.00001:
                        self.apply_two_opt_move(best_sequence, top)
                        best_cost = best_cost + top.cost
                    else:
                        termination_condition = True
                else:
                    termination_condition = True

            iterator = iterator + 1
        return best_sequence, best_cost

    def vnd(self, sequence_of_nodes):
        verbose = False
        best_sequence = sequence_of_nodes[:]
        best_cost = self.calculate_route_cost(best_sequence)
        termination_condition = False
        if len(best_sequence) < 4:
            return best_sequence, best_cost
        
        iterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        move_type = 0
        failed_to_improve = 0
        if verbose:
            print('\nNew Route:')
        while termination_condition is False:
            # SolDrawer.draw(iterator, self.solution, self.allNodes)

            # Relocations
            if move_type == 0:
                rm.initialize()
                self.find_best_relocation_move(best_sequence, rm)
                if rm.cost < -0.00001:
                    self.apply_relocation_move(best_sequence, rm)
                    best_cost = best_cost + rm.cost
                    failed_to_improve = 0
                else:
                    move_type += 1
                    failed_to_improve += 1
            # Swaps
            elif move_type == 1:
                sm.initialize()
                self.find_best_swap_move(best_sequence, sm)
                if sm.cost < -0.00001:
                    self.apply_swap_move(best_sequence, sm)
                    best_cost = best_cost + sm.cost
                    failed_to_improve = 0
                else:
                    move_type += 1
                    failed_to_improve += 1
            # TwoOpt
            elif move_type == 2:
                top.initialize()
                self.find_best_two_opt_move(best_sequence, top)
                if top.cost < -0.00001:
                    self.apply_two_opt_move(best_sequence, top)
                    best_cost = best_cost + top.cost
                    failed_to_improve = 0
                else:
                    move_type = 0
                    failed_to_improve += 1

            if verbose:
                if failed_to_improve > 0:
                    print(f'Trial: {iterator}')
                    print('Failed to improve, now trying:')
                    if move_type == 0:
                        print('relocation')
                    elif move_type == 1:
                        print('swap')
                    elif move_type == 2:
                        print('two opt')
            iterator = iterator + 1

            if failed_to_improve == 3:
                if verbose:
                    print('End\n')
                termination_condition = True

        return best_sequence, best_cost
        
    def optimise_route(self, sequence_of_nodes):
        result, cost = None, None
        if self.optimisation_method == 0:
            result, cost = self.local_search(sequence_of_nodes)
        elif self.optimisation_method == 1:
            result, cost = self.vnd(sequence_of_nodes)
        return result, cost

    def optimise_solution(self, initial_solution):
        # The hard clustered problem will be optimized by rearranging intra cluster nodes, regardless if they belong in
        # the same route. The soft clustered problem will be optimized by rearranging all the nodes in each route,
        # regardless of the cluster they belong.
        optimised_solution = initial_solution.back_up()
        for current_route, route in enumerate(initial_solution.routes):
            if self.hard:
                subroutes = self.create_subroutes(route)
                for current_subroute, subroute in enumerate(subroutes):
                    subroutes[current_subroute], _ = self.optimise_route(subroute)

                optimised_solution.routes[current_route] = [node for subroute in subroutes for node in subroute]
                optimised_solution.cost_per_route[current_route] = self.calculate_route_cost(
                    optimised_solution.routes[current_route])

            else:
                optimised_solution.routes[current_route], optimised_solution.cost_per_route[current_route] \
                    = self.optimise_route(route)
        optimised_solution.total_cost = sum(optimised_solution.cost_per_route)
        return optimised_solution

    def randomise_route(self, sequence_of_nodes):
        randomised_sequence = sequence_of_nodes[:]
        randomised_cost = self.calculate_route_cost(randomised_sequence)
        if len(randomised_sequence) <= 4:
            return randomised_sequence, randomised_cost

        number_of_random_relocations = round(len(randomised_sequence)/3, 0)

        rm = RelocationMove()

        iterator = 1
        while iterator <= number_of_random_relocations:
            rm.initialize()
            current_position = random.randint(1, len(sequence_of_nodes) - 2)
            current_relocated_position = random.randint(1, len(sequence_of_nodes) - 2)

            # do not relocate to the same position
            while current_relocated_position == current_position or current_relocated_position == current_position - 1:
                current_relocated_position = random.randint(1, len(sequence_of_nodes) - 2)

            node_a = sequence_of_nodes[current_position - 1]
            node_b = sequence_of_nodes[current_position]
            node_c = sequence_of_nodes[current_position + 1]

            node_f = sequence_of_nodes[current_relocated_position]
            node_g = sequence_of_nodes[current_relocated_position + 1]

            costs_removed = self.distance_matrix[node_a.ID][node_b.ID] + \
                            self.distance_matrix[node_f.ID][node_g.ID] + \
                            self.distance_matrix[node_b.ID][node_c.ID]

            costs_added = self.distance_matrix[node_f.ID][node_b.ID] + \
                          self.distance_matrix[node_b.ID][node_g.ID] + \
                          self.distance_matrix[node_a.ID][node_c.ID]

            cost = costs_added - costs_removed

            rm.cost = cost
            rm.original_position = current_position
            rm.new_position = current_relocated_position
            self.apply_relocation_move(randomised_sequence, rm)
            randomised_cost += rm.cost
            iterator = iterator + 1
        return randomised_sequence, randomised_cost

    def randomly_select_neighboring_solution(self, solution):
        # The hard clustered problem will be optimized by rearranging intra cluster nodes, regardless if they belong in
        # the same route. The soft clustered problem will be optimized by rearranging all the nodes in each route,
        # regardless of the cluster they belong.
        neighboring_solution = solution.back_up()
        for current_route, route in enumerate(solution.routes):
            if self.hard:
                subroutes = self.create_subroutes(route)
                for current_subroute, subroute in enumerate(subroutes):
                    subroutes[current_subroute], _ = self.randomise_route(subroute)

                neighboring_solution.routes[current_route] = \
                    [node for subroute in subroutes for node in subroute]
                neighboring_solution.cost_per_route[current_route] = self.calculate_route_cost(
                    neighboring_solution.routes[current_route])

            else:
                neighboring_solution.routes[current_route], \
                    neighboring_solution.cost_per_route[current_route] = self.randomise_route(route)
        neighboring_solution.total_cost = sum(neighboring_solution.cost_per_route)
        return neighboring_solution
