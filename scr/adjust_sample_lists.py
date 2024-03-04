# This script reads in the data from the excel file and creates two new files with the ancient and modern samples.
# The ancient samples are samples with an age > 0 and the modern samples are samples with an age < 0.
# Important for the run of this script is:
# The names for the columns in the excel file are:
#  '#',
#  'Genetic ID',
#  'Political Entity',
#  'Lat.',
#  'Long.',
#  'Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]'

import pandas as pd
import os

# get the path for the project directory
parent_dir = os.path.dirname(os.getcwd())

# read in the data from excel file
rawdata = pd.read_excel(f'{parent_dir}/0_data/AADR Annotation.xlsx')
index = rawdata['#']
genetic_id = rawdata['Genetic ID']
countries_list = rawdata['Political Entity']
latitude = rawdata['Lat.']
longitude = rawdata['Long.']
age = rawdata['Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]']

# convert all datalist to string
index = index.astype(str)
genetic_id = genetic_id.astype(str)
countries_list = countries_list.astype(str)
latitude = latitude.astype(str)
longitude = longitude.astype(str)
age = age.astype(str)
            
# create list with anncient and modern samples
ancient_samples = []
modern_samples = []
for i in range(len(index)):
    if int(age[i]) > 0:
        ancient_samples.append([index[i], genetic_id[i], countries_list[i], latitude[i], longitude[i], age[i]])
    else:
        modern_samples.append([index[i], genetic_id[i], countries_list[i], latitude[i], longitude[i], age[i]])
       
# write the data to a new file
with open(f'{parent_dir}/0_data/Ancient_samples_with_labels.txt', 'w') as f:
    f.write('Index\tID\tCountry\tLatitude\tLongitude\tAge\n')
    for sample in ancient_samples:
        f.write('\t'.join(sample) + '\n')
with open(f'{parent_dir}/0_data/Modern_samples_with_labels.txt', 'w') as f:
    f.write('Index\tID\tCountry\tLatitude\tLongitude\tAge\n')
    for sample in modern_samples:
        f.write('\t'.join(sample) + '\n')

        
        