import pandas as pd
from h3 import h3

# funciton that reads the dataframe from a file
def read_df(path):
    df = pd.read_csv(path, sep="\t")
    #convert the age column to numeric
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    return df

# function that reads the ibs matrix with the IBS values and returns the values in a dataframe
def read_dist_matrix(path_matirx, path_id_file):
    id_df = pd.read_csv(path_id_file, sep="\t", header=None, names=["Index","ID"])
    ids = id_df["ID"].tolist()
    dist_matrix = pd.read_csv(path_matirx, sep="\t", header=None, index_col=False, names=ids)
    dist_matrix.index = ids
    return dist_matrix

# this function calculates the average ibs values between two sets of samples
def calc_avg_dist(samples_hex1, samples_hex2, dist_matrix):
    return dist_matrix.loc[samples_hex1, samples_hex2].values.flatten().mean()

# this function calculates the average ibs values between two sets of samples
def calc_avg_dist(samples_hex1, samples_hex2, dist_matrix):
    return dist_matrix.loc[samples_hex1, samples_hex2].values.flatten().mean()

# this function calculates the average ibs between the each hexagon and its neighbors
def calc_neighbor_dist(hexagons, dist_matrix, time_bin_df, hex_col):
    average_distances = {}
    
    # Group the dataframe by the hexagon column and convert each group into a list of IDs, then into a dictionary.
    samples_in_hex = time_bin_df.groupby(hex_col)['ID'].apply(list).to_dict()
    
    # loop through all combinations of hexagons int the time bin and check if there are neighbors
    for i in range (len(hexagons)):
        neighbors = {}
        for j in range (len(hexagons)):
            # if the hexagons are neighbors add their average ibs to the dictionary
            if h3.h3_indexes_are_neighbors(hexagons[i], hexagons[j]):
                Ids_in_hexagon = samples_in_hex.get(hexagons[i], [])
                Ids_in_neighbor = samples_in_hex.get(hexagons[j], [])
                average_ibs_between_hexagons = calc_avg_dist(Ids_in_hexagon, Ids_in_neighbor, dist_matrix)
                # adjust the average ibs to have 5 digits after the decimal point
                average_ibs_between_hexagons = round(average_ibs_between_hexagons, 5)
                neighbors[hexagons[j]] = average_ibs_between_hexagons
                
        average_distances[hexagons[i]] = neighbors

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
        
        # get dataframe for that time bin
        time_bin_df = df[df['AgeGroupTuple'] == time_bin]

        # get all unique hexagons for that time bin
        hexagons = time_bin_df[hex_col].unique()

        # Calculate the average distance for each hexagon to its neighbors within the current time bin.
        average_distances = calc_neighbor_dist(hexagons, dist_matrix, time_bin_df, hex_col)

        # Append the calculated average distances to the list, indexed by the time bin label.
        averages.update({bin_label: average_distances})

    # Return the list of average distances for each time bin.
    return averages
