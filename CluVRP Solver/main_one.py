from SolverPackage import main_functions as mf

"""
Solves a single instance. The file must be a CVRP instance with a VRP-REP compliant format.
Use cmd to run this script or else the prompt asking the instance name will not work.
This script assumes that it is in the same directory with 'Datasets', so change 
the dataset_folder if necessary.
"""

# set dataset directory
datasets = 'Datasets'

# IF NOT USING IN CMD comment the below lines
folder = mf.select_file(datasets, mode='folder')
file = mf.select_file(folder)
# IF NOT USING IN CMD uncomment the below line
# file = 'Datasets\\golden-et-al-1998-set-1\\Golden_01.xml'

# initialize results dictionary
results = {}

# extract instance name
instance_name = mf.get_instance_name(file)
if instance_name.endswith(".xml"):
    instance_name = instance_name[:-4]

# solve and draw instance
number_of_nodes, vehicle_capacity, avg_dem, std_dem, hard_solutions, soft_solutions, hard_times, soft_times =\
    mf.solve_and_draw(instance_name, file, mr_iterations=1, vns_time=1)

# Add the result to the dictionary
results = mf.create_results_dictionary(results, instance_name, number_of_nodes, vehicle_capacity, avg_dem,
                                       std_dem, hard_solutions, soft_solutions, hard_times, soft_times)

print('='*100)

# Save plots and results as a csv file
mf.save_results(results)
