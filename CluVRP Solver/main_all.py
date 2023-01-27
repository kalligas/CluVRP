from SolverPackage import main_functions as mf

"""
Solves all instances in the dataset folder using two VND methods and one VNS method.
The files must be CVRP instances with a VRP-REP compliant format.
This script assumes that it is in the same directory with 'Datasets\\golden-et-al-1998-set-1', so change 
the dataset_folder if necessary.
"""

# set dataset directory
datasets = 'Datasets'

# IF NOT USING IN CMD comment the below line
folder = mf.select_file(datasets, mode='folder')
# IF NOT USING IN CMD uncomment the below line
# folder = 'Datasets\\golden-et-al-1998-set-1'

# get instances' list from dataset folder
file_list = mf.get_file_list(dataset_folder=folder)

# initialize results dictionary
results = {}

# solve all instances
for i, file in enumerate(file_list):

    # extract instance name
    instance_name = mf.get_instance_name(file)

    # Remove the ".xml" extension, if it exists, to save the name of the instance
    # if it does not exist, skip the file
    if instance_name.endswith(".xml"):
        instance_name = instance_name[:-4]
    else:
        continue

    # solve and draw instance
    number_of_nodes, vehicle_capacity, avg_dem, std_dem, hard_solutions, soft_solutions, hard_times, soft_times =\
        mf.solve_and_draw(instance_name, file, mr_iterations=1000, vns_time=60)

    # Add the result to the dictionary
    results = mf.create_results_dictionary(results, instance_name, number_of_nodes, vehicle_capacity, avg_dem, std_dem,
                                           hard_solutions, soft_solutions, hard_times, soft_times)
    # uncomment the below to for first 5 instances
    # if i == 5:
    #     break

print('='*100)

# Save plots and results as a csv file
mf.save_results(results)
