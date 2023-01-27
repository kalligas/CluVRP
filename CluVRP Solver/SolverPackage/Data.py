import xml.etree.ElementTree as Et
import pandas as pd


class Data:

    def __init__(self, file):
        self.file = file
        self.nodes = {}
        self.vehicle_profile = {}

    def extract_data(self):

        tree = Et.parse(self.file)
        nodes_xml = tree.findall('network/nodes/node')
        requests_xml = tree.findall('requests/request')
        fleet_xml = tree.find('fleet/vehicle_profile')

        # Arranging the data in dictionaries
        for node in nodes_xml:
            nid = node.get("id")
            x, y = node.find('cx').text, node.find('cy').text
            self.nodes[nid] = {'x': x, 'y': y, 'type': node.get("type")}

        for request in requests_xml:
            nid = request.get('node')
            demand = request.find('quantity').text
            self.nodes[nid]['demand'] = demand
        self.nodes[str(len(nodes_xml))]['demand'] = 0

        self.vehicle_profile = {
            'departure_node': fleet_xml.find('departure_node').text,
            'arrival_node': fleet_xml.find('arrival_node').text,
            'capacity': fleet_xml.find('capacity').text}

        total_demand = 0
        for _, node in self.nodes.items():
            if int(node['type']) == 1:
                total_demand += float(node['demand'])

        return len(self.nodes)-1, self.vehicle_profile['capacity']

    def get_dem_stats(self):
        nodes_df = pd.DataFrame(self.nodes).transpose().apply(pd.to_numeric, errors='coerce')
        nodes_df.index = nodes_df.index.astype(int)
        avg_dem = nodes_df['demand'].mean()
        std_dem = nodes_df['demand'].std()
        return avg_dem, std_dem
