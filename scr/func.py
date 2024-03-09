import pandas as pd
from h3 import h3

# funciton that reads the dataframe from a file
def read_df(path):
    df = pd.read_csv(path, sep="\t")
    #convert the age column to numeric
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    return df

def calc_avg_dist(samples_hex1, samples_hex2, dist_matrix):
    return dist_matrix.loc[samples_hex1, samples_hex2].values.flatten().mean()

# this function calculates the average ibs between the each hexagon and its neighbors
def calc_neighbor_dist(hexagons, dist_matrix, time_bin_df, hex_col):
    
    # Group the dataframe by the hexagon column and convert each group into a list of IDs, then into a dictionary.
    samples_in_hex = time_bin_df.groupby(hex_col)['ID'].apply(list).to_dict()
    
    # create a dictionary to store the average ibs between each hexagon and its neighbors
    averages = {}
    # loop through all combinations of hexagons int the time bin and check if there are neighbors
    for i in range (len(hexagons)):
        for j in range (i,len(hexagons)):
            # if the hexagons are neighbors add their average ibs to the dictionary
            if h3.h3_indexes_are_neighbors(hexagons[i], hexagons[j]):
                Ids_in_hexagon = samples_in_hex.get(hexagons[i], [])
                Ids_in_neighbor = samples_in_hex.get(hexagons[j], [])
                average_ibs_between_hexagons = calc_avg_dist(Ids_in_hexagon, Ids_in_neighbor, dist_matrix)
                # adjust the average ibs to have 5 digits after the decimal point
                average_ibs_between_hexagons = round(average_ibs_between_hexagons, 5)
                averages[(hexagons[i], hexagons[j])] = average_ibs_between_hexagons
                
    # return dataframe with the average ibs between each hexagon and its neighbors
    return averages

# this function calculates the average ibs between the each hexagon and its neighbors for each time bin
def calc_dist_time_bin(df, dist_matrix=None):
    # get column name for the hexagons
    hex_col = str(df.columns[df.columns.str.contains('hex')][0])
    # Convert the 'AgeGroup' column values to tuples of integers representing the start and end years,
    df['AgeGroupTuple'] = df['AgeGroup'].apply(lambda x: tuple(map(int, x.split('-'))))
    # Sort the unique age group tuples to process them in a chronological order.
    time_bins = sorted(df['AgeGroupTuple'].unique())
    averages = {}
    # Iterate over each time bin.
    for time_bin in time_bins:
        # Format the current time bin as a string for labeling purposes.
        bin_label = rename_times(time_bin)
        
        # get dataframe for that time bin
        time_bin_df = df[df['AgeGroupTuple'] == time_bin]

        # get all unique hexagons for that time bin
        hexagons = time_bin_df[hex_col].unique()
        
        print(f'Processing time bin {bin_label} with {len(hexagons)} unique hexagons...')
        # Calculate the average distance for each hexagon to its neighbors within the current time bin.
        average_distances = calc_neighbor_dist(hexagons, dist_matrix, time_bin_df, hex_col)

        # Append the calculated average distances to the list, indexed by the time bin label.
        averages.update({bin_label: average_distances})

    # Return the list of average distances for each time bin.
    return averages

# function that renames the time bins into a more readable format
def rename_time_bins(df):
    # Convert the 'AgeGroup' column values to tuples of integers representing the start and end years,
    df['AgeGroupTuple'] = df['AgeGroup'].apply(lambda x: tuple(map(int, x.split('-'))))
    # Sort the unique age group tuples to process them in a chronological order.
    time_bins = sorted(df['AgeGroupTuple'].unique())
    renamed_bins = []
    for time_bin in time_bins:
        renamed_bins.append(rename_times(time_bin))
    return renamed_bins

def rename_times(time_bin):
    renamed_years = []
    # get years from time_bin
    for year in time_bin:
        # the time in the dataset is measured from 1950
        if int(year) < 1950:
            year = 1950 - int(year)
            year = str(year) + " a.d."
        else:
            year = int(year) - 1950
            year = str(year) + " b.c."
        renamed_years.append(year)
    return(" - ".join(renamed_years))  # Append to renamed_bins