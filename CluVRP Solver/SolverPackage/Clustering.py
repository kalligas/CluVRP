from sklearn.cluster import KMeans
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

np.random.seed(1)


class Clustering:

    def __init__(self, data):
        self.data = data
        self.nodes_clustered = None
        self.clusters = None
        self.n_clusters = None
        self.km = None
        self.vehicle_profile = data.vehicle_profile

    def build_clusters(self, n_clusters):
        # convert nodes dictionary to pandas dataframe (compatible format with Kmeans algorithm)
        self.nodes_clustered = pd.DataFrame(self.data.nodes).transpose().apply(pd.to_numeric, errors='coerce')
        self.nodes_clustered.index = self.nodes_clustered.index.astype(int)

        # find the depot and add it to the end of the dataframe for easier manipulation
        depot_id = int(self.vehicle_profile['departure_node'])
        depot_row = self.nodes_clustered.loc[depot_id]
        self.nodes_clustered = self.nodes_clustered.drop(depot_id)
        self.nodes_clustered = self.nodes_clustered.append(depot_row).reset_index(drop=True)
        self.nodes_clustered.index = np.arange(1, len(self.nodes_clustered) + 1)
        self.n_clusters = n_clusters

        # clustering (removing the depot beforehand)
        self.km = KMeans(n_clusters=n_clusters, n_init=10)
        depot = self.nodes_clustered.tail(1)
        depot['cluster'] = n_clusters
        self.nodes_clustered.drop(self.nodes_clustered.tail(1).index, inplace=True)
        y_predicted = self.km.fit_predict(self.nodes_clustered[['x', 'y']])
        self.nodes_clustered['cluster'] = y_predicted
        self.nodes_clustered = pd.concat([self.nodes_clustered, depot])
        self.clusters = pd.DataFrame(self.km.cluster_centers_, columns=['x', 'y'])

        # add depot row with its cluster (in which only depot exists) to the dataframe
        depot_row = pd.DataFrame([[0.0, 0.0]], columns=list('xy'), index=[n_clusters])
        self.clusters = pd.concat([self.clusters, depot_row])

        # calculate the demand of each cluster to determine if capacity constraints per vehicle are violated
        clu_dem = self.nodes_clustered.groupby(['cluster'])['demand'].sum()
        if sum(clu_dem > float(self.data.vehicle_profile['capacity'])) == 0:
            return True
        else:
            return False

    def create_clusters(self, initial_number):
        # find feasible number of clusters and build them
        number_of_clusters = initial_number
        possible = False
        while not possible:
            # returns true or false depending on whether the problem is solvable for a given number of clusters
            # the problem is solvable when the vehicle's capacity can meet the demand of every cluster
            # (cluster_demand_i <= vehicle_capacity for every i in [0,number of clusters])
            possible = self.build_clusters(number_of_clusters)
            if possible:
                break
            number_of_clusters += 1
        return number_of_clusters
