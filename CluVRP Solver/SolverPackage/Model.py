import math


class Node:
    def __init__(self, idd, xx, yy, demand, cluster):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.demand = demand
        self.cluster = cluster
        self.cluster_route = None
        self.is_routed = False
        self.neighbors = []


class Route:
    def __init__(self):
        self.sequence_of_nodes = []
        self.cost = 0
        self.load = 0

    def add(self, node, dm, pos=-1):
        self.cost += dm[self.sequence_of_nodes[pos-1].ID][node.ID]
        self.load += node.demand
        self.sequence_of_nodes.insert(pos, node)
        node.is_routed = True


class Cluster:
    def __init__(self, idd, xx, yy):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.nodes = []
        self.demand = 0

    def calc_dem(self):
        self.demand = sum([node.demand for node in self.nodes])


class ClusterRoute:
    def __init__(self, dp, cap):
        self.ID = None
        self.sequence_of_clusters = []
        self.sequence_of_clusters.append(dp)
        self.sequence_of_clusters.append(dp)
        self.node_route = Route()
        self.number_of_customers = 0
        self.cost = 0
        self.capacity = cap
        self.load = 0
        self.nearest_node = None


class Model:
    # instance variables
    def __init__(self, clustering, data):
        self.data = data
        self.clustering = clustering
        self.n_clusters = clustering.n_clusters
        self.all_nodes = []
        self.clusters = []
        self.customers = []
        self.distance_matrix = []
        self.cluster_distance_matrix = []
        self.capacity = None

    def build_model(self):
        # setting up the depot
        depot_id = len(self.clustering.nodes_clustered)
        depot = Node(len(self.clustering.nodes_clustered)-1,
                     self.clustering.nodes_clustered.loc[depot_id, 'x'],
                     self.clustering.nodes_clustered.loc[depot_id, 'y'],
                     0,
                     self.clustering.nodes_clustered.loc[depot_id, 'cluster'])
        depot.is_routed = True

        self.capacity = float(self.data.vehicle_profile['capacity'])

        # setting up the customer Cluster objects
        for i in range(0, self.n_clusters):
            x = self.clustering.clusters.loc[i, 'x']
            y = self.clustering.clusters.loc[i, 'y']
            cluster = Cluster(i, x, y)
            self.clusters.append(cluster)

        # setting up the depot Cluster object
        depot_cluster = Cluster(self.n_clusters,
                                self.clustering.nodes_clustered.loc[depot_id, 'x'],
                                self.clustering.nodes_clustered.loc[depot_id, 'y'])
        depot_cluster.nodes.append(depot)
        self.clusters.append(depot_cluster)

        # setting up the Node objects and adding them to their corresponding cluster
        for i in range(1, len(self.clustering.nodes_clustered)):
            x = self.clustering.nodes_clustered.loc[i, 'x']
            y = self.clustering.nodes_clustered.loc[i, 'y']
            demand = self.clustering.nodes_clustered.loc[i, 'demand']
            cluster_of_node = self.clustering.nodes_clustered.loc[i, 'cluster']
            cust = Node(i-1, x, y, demand, cluster_of_node)
            for cluster in self.clusters:
                if cluster.ID == cluster_of_node:
                    cluster.nodes.append(cust)
            self.all_nodes.append(cust)
            self.customers.append(cust)

        # adding the depot to all_nodes list
        self.all_nodes.append(depot)

        # calculating the demand of each cluster
        for cluster in self.clusters:
            cluster.calc_dem()

        # calculating the distance matrix of the nodes
        rows = len(self.all_nodes)
        self.distance_matrix = [[0.0 for _ in range(rows)] for _ in range(rows)]

        for i in range(0, len(self.all_nodes)):
            for j in range(0, len(self.all_nodes)):
                a = self.all_nodes[i]
                b = self.all_nodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.distance_matrix[i][j] = dist

        # calculating the distance matrix of the cluster centroids
        rows = len(self.clusters)
        self.cluster_distance_matrix = [[0.0 for _ in range(rows)] for _ in range(rows)]

        for i in range(0, len(self.clusters)):
            for j in range(0, len(self.clusters)):
                a = self.clusters[i]
                b = self.clusters[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.cluster_distance_matrix[i][j] = dist
