import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import warnings
import os
warnings.filterwarnings("ignore")


class SolDrawer:

    @staticmethod
    def draw_solutions(name, hard, solutions):
        plot_titles = ['VND', 'VND_MR', 'VNS']
        if hard:
            title_text = '_Hard_'
        else:
            title_text = '_Soft_'
        for current_solution, solution in enumerate(solutions):
            if current_solution == 0:
                SolDrawer.draw_instance(name, solution[0])
            SolDrawer.draw_solution(name + title_text + plot_titles[current_solution] + '_initial', solution[0])
            SolDrawer.draw_solution(name + title_text + plot_titles[current_solution] + '_optimised', solution[1])

    @staticmethod
    def draw_solution(name, sol):
        if not os.path.exists(os.path.join('temp')):
            os.makedirs(os.path.join('temp'))
        plt.clf()
        plt.figure(figsize=(15, 15))
        plt.subplots_adjust(left=0.05, right=0.85, bottom=0.1, top=0.9)
        SolDrawer.draw_points_clustered(sol)
        SolDrawer.draw_routes(sol)
        plt.savefig('temp\\' + name + '_' + str(round(sol.total_cost))+'.jpeg')
        plt.close()

    @staticmethod
    def draw_routes(sol):

        if sol is not None:
            color_pallet = cm.nipy_spectral(np.linspace(0, 1, len(sol.routes)))
            current_route = 1
            for route, current_color in zip(sol.routes, color_pallet):
                x = []
                y = []
                for i in range(0, len(route) - 1):
                    c0 = route[i]
                    c1 = route[i + 1]
                    x.extend([c0.x, c1.x])
                    y.extend([c0.y, c1.y])
                plt.plot(x, y, color=current_color, label='Cluster Route ' + str(current_route))
                current_route += 1
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

    @staticmethod
    def draw_points_clustered(sol):

        clusters = {}
        for route in sol.routes:
            for node in route:
                SolDrawer.add_item(clusters, node.cluster, node)

        color_pallet = cm.nipy_spectral(np.linspace(0, 1, len(clusters)))
        for current_cluster, current_color in zip(range(len(clusters)), color_pallet):
            if len(clusters[current_cluster]) == 1:
                clusters.pop(current_cluster)  # depot cluster
                continue
            x = []
            y = []
            for node in clusters[current_cluster]:
                x.append(node.x)
                y.append(node.y)
            if len(clusters) <= 25:
                plt.scatter(x, y, color=current_color, label='Cluster ' + str(current_cluster+1))
                plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
            else:
                plt.scatter(x, y, color=current_color)

    @staticmethod
    def draw_points(sol):
        clusters = {}
        for route in sol.routes:
            for node in route:
                # if node.x != 0 and node.y != 0:
                SolDrawer.add_item(clusters, node.cluster, node)

        color_pallet = cm.nipy_spectral(np.linspace(0, 1, len(clusters)))
        x = []
        y = []
        for current_cluster, current_color in zip(range(len(clusters)), color_pallet):
            if len(clusters[current_cluster]) == 1:
                clusters.pop(current_cluster)  # depot cluster
                continue
            for node in clusters[current_cluster]:
                x.append(node.x)
                y.append(node.y)

        plt.scatter(x, y, color='black')

    @staticmethod
    def draw_instance(name, sol):
        plt.clf()
        plt.figure(figsize=(15, 15))
        plt.subplots_adjust(left=0.05, right=0.85, bottom=0.1, top=0.9)
        SolDrawer.draw_points(sol)
        plt.savefig('temp\\' + name + '_' + 'points' + '.jpeg')
        plt.close()
        plt.clf()
        plt.figure(figsize=(15, 15))
        plt.subplots_adjust(left=0.05, right=0.85, bottom=0.1, top=0.9)
        SolDrawer.draw_points_clustered(sol)
        plt.savefig('temp\\' + name + '_' + 'clustered_points' + '.jpeg')
        plt.close()

    @staticmethod
    def add_item(d, key, item):
        if key in d:
            d[key].append(item)
        else:
            d[key] = [item]
