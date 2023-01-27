from .Data import *
from .Clustering import *
from .Solver import *
from .SolDrawer import *
import time
import datetime
from PyInquirer import prompt

"""
Contains all the functions needed for main_one.py and main_all.py to run.
"""


def get_file_list(dataset_folder='Datasets', mode='file'):
    # Get the current working directory
    current_dir = os.getcwd()
    my_list = []

    # Walk through all the files and directories in the directory
    for dir_name, subdir_list, file_list in os.walk(current_dir):
        # Check if the current directory is the "Datasets" folder
        if dir_name == current_dir + '\\' + dataset_folder:
            # Loop through all the files in the "Datasets" folder
            if mode == 'file':
                it_list = file_list
            else:
                it_list = subdir_list
            for name in it_list:
                # Add the file to the list
                my_list.append(dataset_folder + '\\' + name)

    return my_list


def select_file(dataset_folder, mode='file'):
    file_list = get_file_list(dataset_folder=dataset_folder, mode=mode)
    questions = [
        {
            'type': 'list',
            'name': 'selected_option',
            'message': 'Please select a Folder:',
            'choices': file_list,
        }
    ]
    answers = prompt(questions)
    print(f"You selected {answers['selected_option']}")
    file = answers['selected_option']
    return file


def get_instance_name(file):
    # Split the file directory string into a list of levels
    levels = file.split(os.sep)

    # Get the last level
    instance_name = levels[-1]
    return instance_name


def solve_and_draw(instance_name, file, mr_iterations=2000, mr_limit=500, vns_time=60, detailed_print=False):
    """
    Uses all the classes from SolverPackage to extract data from current instance, create clusters for which the problem
    is solvable, create the necessary objects (for storing information regarding each node, route, cluster, cluster
    route), solve the hard-clustered and soft-clustered CluVrp problem (using the get solutions function, defined later)
    , and draw the solutions
    """

    if not os.path.exists(os.path.join('temp')):
        os.makedirs(os.path.join('temp'))

    print('\n'+'='*100)
    print(f'Solving {file}...\n')

    # starting number of clusters (will probably change to create clusters of feasible demand)
    initial_number_of_clusters = 10

    # extract the data from the xml file and return number of nodes and vehicle capacity
    data = Data(file)
    number_of_nodes, vehicle_capacity = data.extract_data()
    avg_dem, std_dem = data.get_dem_stats()

    # convert the CVRP instance to a CluVRP instance
    cl = Clustering(data)
    num = cl.create_clusters(initial_number_of_clusters)
    if detailed_print:
        print(f'  Number of clusters for which the problem is solvable: {num}')

    # create the model of the problem (all classes, distance matrices)
    m = Model(cl, data)
    m.build_model()

    # initialize solver and solve the problem
    s = Solver(m)

    # get the solutions
    hard_solutions, hard_times = get_solutions(s, hard=True, mr_iterations=mr_iterations, mr_limit=mr_limit,
                                               vns_time=vns_time)
    soft_solutions, soft_times = get_solutions(s, hard=False, mr_iterations=mr_iterations, mr_limit=mr_limit,
                                               vns_time=vns_time)

    # draw solutions
    SolDrawer.draw_solutions(instance_name, hard=True, solutions=hard_solutions)
    SolDrawer.draw_solutions(instance_name, hard=False, solutions=soft_solutions)

    # save routes to txt
    save_routes(instance_name, hard=True, solutions=hard_solutions)
    save_routes(instance_name, hard=False, solutions=soft_solutions)

    return number_of_nodes, vehicle_capacity, avg_dem, std_dem, hard_solutions, soft_solutions, hard_times, soft_times


def save_results(results):
    """
    Saves results to a csv file, and also moves the results and plots from 'temp' folder to 'Plots_Results' folder, in a
    sub-folder based on date and time.
    :param results: dictionary with the results
    :return:
    """

    # Create a DataFrame from the nested dictionary
    results = pd.DataFrame.from_dict(results, orient='index')

    # Convert all values to numeric
    results = results.applymap(lambda x: pd.to_numeric(x, errors='coerce'))

    # round the values to 4 decimal places
    results = results.applymap(lambda x: round(x, 4))

    # Write the DataFrame to a CSV file
    results.to_csv('temp\\results.csv', index=False)

    # get current date and time
    now = datetime.datetime.now()

    # create the folder 'Plots_Results' if it doesn't already exist
    if not os.path.exists('Plots_Results'):
        os.makedirs('Plots_Results')

    # create a sub-folder named after the current date and time in the 'Plots_Results' folder
    date_time_folder = now.strftime('%Y-%m-%d %H-%M-%S')
    date_time_folder = date_time_folder.replace("-", "").replace(" ", "_")
    if not os.path.exists(os.path.join('Plots_Results', date_time_folder)):
        os.makedirs(os.path.join('Plots_Results', date_time_folder))

    # move all jpeg files into the sub-folder along with the results
    for file in os.scandir('temp'):
        if file.name.endswith(".jpeg") or file.name.startswith('results'):
            os.rename(file.path, os.path.join('Plots_Results', date_time_folder, file.name))

    os.removedirs('temp')


def get_solutions(s, hard=True, detailed_print=False, mr_iterations=2000, mr_limit=500, vns_time=60):
    """
    Gets two VND solutions (two different initial solution construction algorithms) and one VNS solution
    :param s: Solver object that contains the methods for solving CluVrp
    :param hard: Parameter indicating to solve the problem as hard or soft clustered
    :param detailed_print: Print details (routes, costs etc.)
    :param mr_iterations: iterations for the vnd_mr method
    :param mr_limit: iterations without improvement after which the program stops for the vnd_mr method
    :param vns_time: execution time of vns
    :return: solutions and respective run times
    """
    # vnd
    if hard:
        text = 'Hard-clustered'
    else:
        print('-' * 100+'\n')
        text = 'Soft-clustered'
    print(f'  {text} VND:')
    start_time = time.perf_counter()
    vnd_nn_solution = s.vnd(hard=hard, construction_method=0, detailed_print=detailed_print)
    end_time = time.perf_counter()
    vnd_nn_time = end_time - start_time

    # vnd_mr, initial solutions with nearest neighbor rcl algorithm, rcl length = 3
    if hard:
        text = 'Hard-clustered'
    else:
        text = 'Soft-clustered'
    print(f'  {text} VND Multiple restarts, initial solutions with nearest neighbor rcl algorithm (rcl length = 3):')
    start_time = time.perf_counter()
    vnd_mr_solution = s.vnd_mr(hard=hard, full_random_initial_solutions=False, mr_iterations=mr_iterations,
                               mr_limit=mr_limit, detailed_print=detailed_print)
    end_time = time.perf_counter()
    vnd_mr_time = end_time - start_time

    # vns
    if hard:
        text = 'Hard-clustered'
    else:
        text = 'Soft-clustered'
    print(f'  {text} VNS')
    start_time = time.perf_counter()
    vns_solution = s.vns(hard=hard, detailed_print=detailed_print, vns_time=vns_time)
    end_time = time.perf_counter()
    vns_time = end_time - start_time

    # store solutions and times
    solutions = (vnd_nn_solution, vnd_mr_solution, vns_solution)
    times = (vnd_nn_time, vnd_mr_time, vns_time)

    return solutions, times


def create_results_dictionary(results, instance_name, number_of_nodes, vehicle_capacity, avg_dem, std_dem,
                              hard_solutions, soft_solutions, hard_times, soft_times):
    # A = Hard-Clustered VND, B = Hard-Clustered Multiple Restart VND, C = Hard-Clustered VNS
    # D = Soft-Clustered VND, E = Soft-Clustered Multiple Restart VND, F = Soft-Clustered VNS
    results[instance_name] = {'Number of nodes': number_of_nodes, 'Vehicle Capacity': vehicle_capacity,
                              'Average node demand': avg_dem, 'St.Dev.': std_dem,
                              'I_Cost': hard_solutions[0][0].total_cost,
                              'A_Cost': hard_solutions[0][1].total_cost, 'A_Time': hard_times[0],
                              'B_Cost': hard_solutions[1][1].total_cost, 'B_Time': hard_times[1],
                              'C_Cost': hard_solutions[2][1].total_cost, 'C_Time': hard_times[2],
                              'D_Cost': soft_solutions[0][1].total_cost, 'D_Time': soft_times[0],
                              'E_Cost': soft_solutions[1][1].total_cost, 'E_Time': soft_times[1],
                              'F_Cost': soft_solutions[2][1].total_cost, 'F_Time': soft_times[2]
                              }
    return results


def save_routes(name, hard, solutions):
    plot_titles = ['VND', 'VND_MR', 'VNS']
    if hard:
        title_text = '_Hard_'
    else:
        title_text = '_Soft_'
    for current_solution, solution in enumerate(solutions):
        route_name = name + title_text + plot_titles[current_solution]
        solution[0].save_to_txt(route_name + '_initial')
        solution[1].save_to_txt(route_name + '_optimised')
