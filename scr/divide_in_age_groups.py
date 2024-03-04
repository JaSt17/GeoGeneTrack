# This script reads the ancient samples with labels and divides them into age groups.
# The age groups are created by dividing the samples into n bins with an equal number of samples in each group.
# The age group is then added to the dataframe and written to a file.

import pandas as pd
import os
import sys

def read_df(path):
    df = pd.read_csv(path, sep="\t")
    #convert the age column to numeric
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    return df
 
# function that creates n time bins with equally distributed number of samples in each group
def create_age_groups(df, number_of_bins=30):
    total_samples = df.shape[0]
    sample_per_bin, remainder = divmod(total_samples, number_of_bins)
    temp_df = df.sort_values('Age')
    age_groups = []
    start_index = 0
    # iterate over the number of bins
    for bin_num in range(number_of_bins):
        # Calculate the end index for the current bin; add an extra sample to some bins to distribute the remainder
        if remainder > 0:
            end_index = start_index + sample_per_bin + 1
            remainder -= 1
        else:
            end_index = start_index + sample_per_bin
        
        # Append the subset of the dataframe corresponding to the current bin
        age_groups.append(temp_df.iloc[start_index:end_index])
        
        # Update the start index for the next bin
        start_index = end_index
        
    return age_groups

# function that creates a name for each age group
def name_age_groups(age_groups):
    name_dict = {}
    for group in age_groups:
        min_age = group['Age'].min()
        max_age = group['Age'].max()
        for i in range(len(group)):
            id = group.iloc[i]['ID']
            name_dict[id] = f"{min_age}-{max_age}"
    return name_dict

# function that adds the age group to the dataframe
def add_age_group_column(df, name_dict):
    df['AgeGroup'] = df['ID'].map(name_dict)
    return df

# function that writes the age groups to a file
def write_df(df, path):
    df.to_csv(path, sep="\t", index=False)
    return

# get the path for the project directory
parent_dir = os.path.dirname(os.getcwd())

def main():
    df = read_df(f'{parent_dir}/0_data/Ancient_samples_with_labels.txt')
    # if there is an argument, use it as the number of bins, otherwise use the default value 30
    if sys.argv[1] is not None:
        number_of_bins = int(sys.argv[1])
        age_groups = create_age_groups(df, number_of_bins)
    else:
        age_groups = create_age_groups(df)
    # get the name for each age group
    name_dict = name_age_groups(age_groups)
    # create a new dataframe with the age group column
    new_df = add_age_group_column(df, name_dict)
    # write the dataframe to a file
    write_df(new_df, f'{parent_dir}/0_data/Ancient_samples_with_age_group.txt')