import h3
import pandas as pd
import pickle


# function that reads the ibs matrix with the IBS values and returns the values in a dataframe
def read_dist_matrix(path, path_matrix, path_id_file, resolutuion, time_bins):
    # check if a saved ibs matrix for the given time bins and resolution exists
    try:
        dist_matrix = pickle.load(open(f"{path}/4_dist_matrix/dist_matrix_{time_bins}_{resolutuion}.p", "rb"))
        print("Distance matrix loaded from file.")
        return dist_matrix
    except:
        # Load the ID file to get the order of IDs in the distance matrix.
        id_df = pd.read_csv(path_id_file, sep="\t", header=None, names=["Index", "ID"])
        # Get the IDs as a list to use as column and index names for the distance matrix.
        ids = id_df["ID"].tolist()
        # This assumes the order of IDs in the ID file matches the order in the distance matrix file.
        dist_matrix = pd.read_csv(path_matrix, sep="\t", header=None, index_col=False, names=ids)
        dist_matrix.index = ids
        # save the distance matrix as a pickle file
        pickle.dump(dist_matrix, open(f"{path}/4_dist_matrix/dist_matrix_{time_bins}_{resolutuion}.p", "wb"))
        # return the distance matrix as a dataframe
        return dist_matrix

# this function calculates the average ibs values between two sets of samples
def calc_avg_dist(samples_hex1, samples_hex2, dist_matrix):
    return dist_matrix.loc[samples_hex1, samples_hex2].values.flatten().mean()

# this function calculates the average ibs between the each hexagon and its neighbors
def calc_neighbor_dist(hexagons, dist_matrix, df, hex_col):
    average_distances = {}
    
    # Use a dictionary comprehension to create a mapping of each hexagon to its neighbors.
    # h3.k_ring_distances(hexagon, 1)[1] gets the neighbors one ring out from each hexagon.
    all_neighbors = {hexagon: h3.k_ring_distances(hexagon, 1)[1] for hexagon in hexagons}

    # Group the dataframe by the hexagon column and convert each group into a list of IDs, then into a dictionary.
    samples_in_hex = df.groupby(hex_col)['ID'].apply(list).to_dict()

    # Iterate over each hexagon and its neighbors.
    for hexagon, neighbors in all_neighbors.items():
        neighbor_dist = {}

        # Retrieve the list of IDs within the current hexagon
        Ids_in_hexagon = samples_in_hex.get(hexagon, [])

        # Iterate over each neighbor of the current hexagon.
        for neighbor in neighbors:
            # Retrieve the list of IDs within the neighbor hexagon
            Ids_in_neighbor = samples_in_hex.get(neighbor, [])
            if Ids_in_neighbor:
                # Calculate the average distance between IDs in the current hexagon and IDs in the neighbor hexagon.
                dist_to_hexagon = calc_avg_dist(Ids_in_hexagon, Ids_in_neighbor, dist_matrix)

                # Store the calculated average distance.
                neighbor_dist[neighbor] = dist_to_hexagon

        # Update the main dictionary with the ibs from the current hexagon to its neighbors.
        average_distances[hexagon] = neighbor_dist

    # Return the dictionary containing average ibs from each hexagon to its neighbors.
    return average_distances

# this function calculates the average ibs between the each hexagon and its neighbors for each time bin
def calc_dist_time_bin(df, hex_col, dist_matrix):
    # Convert the 'AgeGroup' column values to tuples of integers representing the start and end years,
    df['AgeGroupTuple'] = df['AgeGroup'].apply(lambda x: tuple(map(int, x.split('-'))))

    # Sort the unique age group tuples to process them in a chronological order.
    time_bins = sorted(df['AgeGroupTuple'].unique())

    # Initialize a list to hold the average ibs calculations for each time bin.
    averages = {}

    # Iterate over each time bin.
    for time_bin in time_bins:
        # Format the current time bin as a string for labeling purposes.
        bin_label = f"{time_bin[0]}-{time_bin[1]}"

        # Select hexagons that fall into the current time bin.
        hexagons = df[df['AgeGroupTuple'] == time_bin][hex_col].unique()

        # Calculate the average distance for each hexagon to its neighbors within the current time bin.
        average_distances = calc_neighbor_dist(hexagons, dist_matrix, df, hex_col)

        # Append the calculated average distances to the list, indexed by the time bin label.
        averages.update({bin_label: average_distances})

    # Return the list of average distances for each time bin.
    return averages

# this function returns the hexagons that have an average ibs to their neighbors below a certain threshold
def calc_hexagons_below_threshold(averages, threshold):
    hexagons_below_threshold = {}
    
    # Iterate over each time_bin dictionary in the averages list
    for time_bin_dict in averages:
        for time_bin, hexagons in time_bin_dict.items():
            # Initialize a list to store hexagon, neighbor, and ibs info for this time_bin
            entries = []
            
            # Iterate over each hexagon and its neighbors within the current time_bin
            for hexagon, neighbors in hexagons.items():
                for neighbor, ibs in neighbors.items():
                    # Check if the ibs is below the threshold
                    if ibs < threshold:
                        # Prepare the entry containing the hexagon, its neighbor, and the distance
                        entry = [hexagon, neighbor, ibs]
                        entries.append(entry)
            
            # Update the dictionary only if there are entries below the threshold for this time_bin
            if entries:
                hexagons_below_threshold[time_bin] = entries

    return hexagons_below_threshold

# this function writes the hexagons that have an average ibs to their neighbors below a certain threshold to a file
def write_output(hexagons_below_threshold, threshold, output_file):
    with open(output_file, 'w') as f:
        f.write(f"TimeBin\tHexagon\tNeighbor\tDistance\t(Threshold: <{threshold})\n")
        for time_bin, entries in hexagons_below_threshold.items():
            for entry in entries:
                f.write(f"{time_bin}\t{entry[0]}\t{entry[1]}\t{entry[2]}\n")
    
# this function reads in the ibs matrix and the id file and returns a df with holds the pairwise ibs for all samples
def calc_distance_matrix(path, df, dist_matrix, id_file, resolutuion, time_bins):
    hex_col = df.columns[7]
    dist_matrix = read_dist_matrix(path, dist_matrix, id_file, resolutuion, time_bins)
    distances_in_each_time_bin = calc_dist_time_bin(df, hex_col, dist_matrix)
    return distances_in_each_time_bin
    
# this function writes the hexagons that have an average ibs to their neighbors below a certain threshold to a file and returns a dict with time bins as keys and hexagons as values
def get_hexagons_below_threshold(path, distances_in_each_time_bin, threshold):
    hexagons_below_threshold = calc_hexagons_below_threshold(distances_in_each_time_bin, threshold)
    write_output(hexagons_below_threshold, threshold, f"{path}/output/output_{threshold}.txt")
    return hexagons_below_threshold


    
    