import h3
import pandas as pd
import sys

# function that reads the data from a file and returns a dataframe
def read_df(path):
    df = pd.read_csv(path, sep="\t")
    #convert the age column to numeric
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    return df

# function that reads the distance matrix with the IBS distances and returns a distance matrix as a dataframe
def read_dist_matrix(path_matrix, path_id_file):
    # Load the ID file to get the order of IDs in the distance matrix.
    id_df = pd.read_csv(path_id_file, sep="\t", header=None, names=["Index", "ID"])
    # Get the IDs as a list to use as column and index names for the distance matrix.
    ids = id_df["ID"].tolist()
    # This assumes the order of IDs in the ID file matches the order in the distance matrix file.
    dist_matrix = pd.read_csv(path_matrix, sep=" ", header=None, index_col=False, names=ids)
    dist_matrix.index = ids
    # return the distance matrix as a dataframe
    return dist_matrix

# this function calculates the average distance between two sets of samples
def calc_avg_dist(samples_hex1, samples_hex2, dist_matrix):
    return dist_matrix.loc[samples_hex1, samples_hex2].values.flatten().mean()

# this function calculates the average distance between the each hexagon and its neighbors
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

        # Update the main dictionary with the distances from the current hexagon to its neighbors.
        average_distances[hexagon] = neighbor_dist

    # Return the dictionary containing average distances from each hexagon to its neighbors.
    return average_distances

# this function calculates the average distance between the each hexagon and its neighbors for each time bin
def calc_dist_time_bin(df, hex_col, dist_matrix):
    # Convert the 'AgeGroup' column values to tuples of integers representing the start and end years,
    df['AgeGroupTuple'] = df['AgeGroup'].apply(lambda x: tuple(map(int, x.split('-'))))

    # Sort the unique age group tuples to process them in a chronological order.
    time_bins = sorted(df['AgeGroupTuple'].unique())

    # Initialize a list to hold the average distances calculations for each time bin.
    averages = []

    # Iterate over each time bin.
    for time_bin in time_bins:
        # Format the current time bin as a string for labeling purposes.
        bin_label = f"{time_bin[0]}-{time_bin[1]}"

        # Select hexagons that fall into the current time bin.
        hexagons = df[df['AgeGroupTuple'] == time_bin][hex_col].unique()

        # Calculate the average distance for each hexagon to its neighbors within the current time bin.
        average_distances = calc_neighbor_dist(hexagons, dist_matrix, df, hex_col)

        # Append the calculated average distances to the list, indexed by the time bin label.
        averages.append({bin_label: average_distances})

    # Return the list of average distances for each time bin.
    return averages

# this function returns the hexagons that have an average distance to their neighbors below a certain threshold
def get_hexagons_below_threshold(averages, threshold):
    hexagons_below_threshold = {}
    
    # Iterate over each time_bin dictionary in the averages list
    for time_bin_dict in averages:
        for time_bin, hexagons in time_bin_dict.items():
            # Initialize a list to store hexagon, neighbor, and distance info for this time_bin
            entries = []
            
            # Iterate over each hexagon and its neighbors within the current time_bin
            for hexagon, neighbors in hexagons.items():
                for neighbor, distance in neighbors.items():
                    # Check if the distance is below the threshold
                    if distance < threshold:
                        # Prepare the entry containing the hexagon, its neighbor, and the distance
                        entry = [hexagon, neighbor, distance]
                        entries.append(entry)
            
            # Update the dictionary only if there are entries below the threshold for this time_bin
            if entries:
                hexagons_below_threshold[time_bin] = entries

    return hexagons_below_threshold

# inputs:
# 1. path to the file containing the ancient data with location and time information
# 2. path to the file containing the distance matrix
# 3. path to the file containing the IDs corresponding to the distance matrix
# 4. threshold for the average distance to the neighbors        
if __name__ == "__main__":
    df = read_df(sys.argv[1])
    hex_col = df.columns[7]
    dist_matrix = read_dist_matrix(sys.argv[2], sys.argv[3])
    distances_in_each_time_bin = calc_dist_time_bin(df, hex_col, dist_matrix)
    hexagons_below_threshold = get_hexagons_below_threshold(distances_in_each_time_bin, float(sys.argv[4]))
    
    