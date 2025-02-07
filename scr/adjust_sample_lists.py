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

def split_ancient_modern(path):
    # read in the data from excel file
    rawdata = pd.read_excel(f'{path}/0_data/AADR Annotation.xlsx')
    index = rawdata['#']
    genetic_id = rawdata['Genetic ID']
    countries_list = rawdata['Political Entity']
    latitude = rawdata['Lat.']
    longitude = rawdata['Long.']
    age = rawdata['Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]']

    # convert all data list to string
    index = index.astype(str)
    genetic_id = genetic_id.astype(str)
    countries_list = countries_list.astype(str)
    latitude = latitude.astype(str)
    longitude = longitude.astype(str)
    age = age.astype(str)
                
    # create list with ancient and modern samples
    ancient_samples = []
    modern_samples = []
    for i in range(len(index)):
        if int(age[i]) > 0:
            ancient_samples.append([index[i], genetic_id[i], countries_list[i], latitude[i], longitude[i], age[i]])
        else:
            modern_samples.append([index[i], genetic_id[i], countries_list[i], latitude[i], longitude[i], age[i]])
        
    # write the data to a new file
    with open(f'{path}/0_data/Ancient_samples.txt', 'w') as f:
        f.write('Index\tID\tCountry\tLatitude\tLongitude\tAge\n')
        for sample in ancient_samples:
            f.write('\t'.join(sample) + '\n')
    with open(f'{path}/0_data/Modern_samples.txt', 'w') as f:
        f.write('Index\tID\tCountry\tLatitude\tLongitude\tAge\n')
        for sample in modern_samples:
            f.write('\t'.join(sample) + '\n')
    # write the ID's of the ancient samples to a new file (for the run of the next script with plink)
    with open(f'{path}/0_data/keep_id_list.txt', 'w') as f:
        f.write('Index\tID\n')
        for sample in ancient_samples:
            f.write('\t'.join(sample[:2]) + '\n')
            

        
        