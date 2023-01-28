import pandas as pd
from .Model import *


class Vrp:
    def __init__(self, m):
        self.clusters = m.clusters
        self.cluster_distance_matrix = m.cluster_distance_matrix
        self.n_clusters = m.n_clusters
        self.capacity = m.capacity

    def clarke_wright(self, cluster_routes):
        """Solves the high level problem of assigning vehicles to the clusters."""
        
        # STEP 1: Calculate the savings s(i,j) =  d(D,i) + d(D,j) - d(i,j) for every pair (i,j) of demand points
        n_clu = self.n_clusters
        savings = []
        pairs = []
        for i in range(0, len(self.clusters) - 1):
            for j in range(i + 1, len(self.clusters) - 1):
                pairs.append((i, j))
                savings.append(self.cluster_distance_matrix[0][i] +
                               self.cluster_distance_matrix[0][j] -
                               self.cluster_distance_matrix[i][j])

        # STEP 2: Sort savings
        savings_df = pd.DataFrame([savings, pairs]).transpose()
        savings_df.columns = ['savings', 'pairs']
        savings_df = savings_df.sort_values('savings', ascending=False)
        savings_df = savings_df.loc[savings_df.savings > 0]

        # STEP 3: Merge routes considering capacity constraints
        current_route = 0
        for i in range(len(savings_df)):
        
            # storing the two cluster nodes from the savings pair to clu1 and clu2
            clu1 = savings_df.iloc[i, 1][0]
            clu2 = savings_df.iloc[i, 1][1]
            
            # create the first route with the highest saving considering capacity constrains
            if not cluster_routes:
                if (self.clusters[clu1].demand + self.clusters[clu2].demand) < self.capacity:
                    cluster_routes.append(ClusterRoute(n_clu, self.capacity))
                    cluster_routes[current_route].sequence_of_clusters[1:1] = [clu1, clu2]
                    cluster_routes[current_route].load = self.clusters[clu1].demand + self.clusters[clu2].demand
                    current_route += 1
                    continue

            # merge routes considering capacity constraints and cluster nodes that are already routed
            else:
                for route in cluster_routes:
                    # is cluster 1 already in the route?
                    clu1_in_route = clu1 in route.sequence_of_clusters
                    
                    # is cluster 2 already in the route?
                    clu2_in_route = clu2 in route.sequence_of_clusters
                    
                    # if only one of them is in the route, start considering the merge
                    if clu1_in_route ^ clu2_in_route:
                        already_routed = False
                        
                        # now check if these clusters are already merged with other clusters
                        for check_route in cluster_routes:
                            if clu1_in_route:
                                if clu2 in check_route.sequence_of_clusters:
                                    already_routed = True
                            elif clu2_in_route:
                                if clu1 in check_route.sequence_of_clusters:
                                    already_routed = True
                                    
                        # if they are already merged with other clusters, stop considering the merge
                        if already_routed:
                            continue
                        route_length = len(route.sequence_of_clusters)

                        # the nodes considered for merging must not be interior nodes, not considering the depot 
                        # as an exterior node
                        cond1 = route_length > 4 and not any(value in route.sequence_of_clusters[2:route_length - 2]
                                                             for value in [clu1, clu2])
                        # if the route length is <= 4, then the customer nodes in it are not interior                                    
                        cond2 = route_length <= 4

                        # condition to insert the second cluster node in the route
                        insert_clu2 = (cond1 or cond2) and clu1_in_route
                        
                        # condition to insert the first cluster node in the route
                        insert_clu1 = (cond1 or cond2) and clu2_in_route

                        # actions to take when inserting the second cluster of the pair
                        if insert_clu2:

                            if (self.clusters[clu2].demand + route.load) < self.capacity:
                                if route.sequence_of_clusters[1] == clu1:
                                    route.sequence_of_clusters.insert(1, clu2)
                                else:
                                    route.sequence_of_clusters.insert(route_length-1, clu2)
                                route.load += self.clusters[clu2].demand
                                break
                            else:
                                continue

                        # actions to take when inserting the first cluster of the pair
                        elif insert_clu1:

                            if (self.clusters[clu1].demand + route.load) < self.capacity:
                                if route.sequence_of_clusters[1] == clu2:
                                    route.sequence_of_clusters.insert(1, clu1)
                                else:
                                    route.sequence_of_clusters.insert(route_length - 1, clu1)
                                route.load += self.clusters[clu1].demand
                                break
                            else:
                                continue
                    else:
                        continue

                # if the cluster nodes of the savings pair are not in any route, and capacity constraints are not
                # violated, create a new cluster route
                if not any(value in route.sequence_of_clusters
                             for value in [clu1, clu2]
                             for route in cluster_routes):

                    if (self.clusters[clu1].demand + self.clusters[clu2].demand) <= self.capacity:
                        cluster_routes.append(ClusterRoute(n_clu, self.capacity))
                        cluster_routes[current_route].sequence_of_clusters[1:1] = [clu1, clu2]
                        cluster_routes[current_route].load = self.clusters[clu1].demand + self.clusters[clu2].demand
                        current_route += 1

        # Check that no common cluster nodes exist in the routes
        routes_set_list = []
        for route in cluster_routes:
            for cluster in route.sequence_of_clusters:
                routes_set_list.append(cluster)
        duplicates = []
        for num in routes_set_list:
            if routes_set_list.count(num) > 1 and num != n_clu:
                if num not in duplicates:
                    duplicates.append(num)
        if not duplicates:
            pass
        else:
            print(f'  Some Clusters were not routed only once!'
                  f'  Clusters:{duplicates}')

        # Get solo routes (routes that serve one cluster node only)
        # exclude depot (n_clu -1)
        solo_routes = []
        setlist = [set(route.sequence_of_clusters) for route in cluster_routes]
        for i in range(0, n_clu):
            check = []
            for my_set in setlist:
                check.append((i in my_set))
            if any(check):
                pass
            else:
                solo_routes.append(i)

        # create solo routes
        for i, solo_route in enumerate(solo_routes):
            cluster_routes.append(ClusterRoute(n_clu, self.capacity))
            cluster_routes[current_route + i].sequence_of_clusters[1:1] = [solo_route]
            cluster_routes[current_route + i].load = self.clusters[solo_route].demand

        missed = []
        for cluster in range(n_clu):
            if cluster not in routes_set_list:
                missed.append(cluster)
        if not missed:
            print(f'  Some Clusters were missed!'
                  f'  Clusters:{missed}')

        # replace cluster numbers with the respective objects and add cluster_route ID
        # and add cluster_route id to each node
        for idd, route in enumerate(cluster_routes[:]):
            route.ID = idd
            for i, cluster in enumerate(route.sequence_of_clusters[:]):
                route.sequence_of_clusters[i] = self.clusters[cluster]
                for node in self.clusters[cluster].nodes:
                    node.cluster_route = idd
                    
        return cluster_routes
