from adjust_sample_lists import split_ancient_modern
import pickle
import os
import pandas as pd

# this function reads the distance matrix from the mibs file and saves it as a pickle file
# this allows for fast reading of the matrix in the future
def read_dist_matrix(path):
    path_matirx = path+"/3_ibs_dist/ibs_dist.mibs"
    path_id_file = path_matirx + ".id"
    id_df = pd.read_csv(path_id_file, sep="\t", header=None, names=["Index","ID"])
    ids = id_df["ID"].tolist()
    dist_matrix = pd.read_csv(path_matirx, sep="\t", header=None, index_col=False, names=ids)
    dist_matrix.index = ids
    pickle_path = path_matirx + ".pkl"
    dist_matrix.to_pickle(pickle_path)

# this function runs the initial steps of the pipeline:
# 1. split the ancient and modern samples
# 2. write ancient samples with time bins and hexagon ids to plink format
# 3. calculate ibs distance matrix
# 4. write the distance matrix to a pickle file
# it only has to be run once or if the data changes or we want to add additional plink filtering steps
def initial_run():
    # get the path for the project directory
    path = os.getcwd()
    
    print("Running GeoGeneTrack")
    print("filtering ancient and modern samples...")
    split_ancient_modern(path)
    
    print("write ancient samples with time bins and hexagon ids to plink format...")
    os.system(f"cd {path}")
    os.system("mkdir 1_ancient_data")
    os.system(f"plink --bfile 0_data/samples --keep 0_data/keep_id_list.txt --make-bed --out 1_ancient_data/ancient_samples")
    print("calculating ibs distance matrix...")
    os.system(f"cd {path}")
    os.system("mkdir 3_ibs_dist")
    os.system(f"plink --bfile 1_ancient_data/ancient_samples --distance ibs flat-missing --out 3_ibs_dist/ibs_dist")
    
    print("reading distance matrix...")
    read_dist_matrix(path)
    print("done")
    
if __name__ == "__main__":
    initial_run()
    