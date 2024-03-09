from adjust_sample_lists import split_ancient_modern
from label_samples_time_hexa import label_samples, read_df
from calc_distances import calc_distance_matrix, get_hexagons_below_threshold
import pickle
import os

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
# it only has to be run once or if the data changes or we want to add aditional plink filtering steps
def initial_run():
    # get the path for the project directory
    path = os.getcwd()
    
    print("Running GeoGeneTrack")
    print("filtering ancient and modern samples...")
    split_ancient_modern(path)
    
    print("write ancient samples with time bins and hexagon ids to plink format...")
    os.system(f"cd {path}")
    os.system(f"plink --bfile 0_data/samples --keep 0_data/keep_id_list.txt --make-bed --out 1_ancient_data/ancient_samples")
    print("calculating ibs distance matrix...")
    os.system(f"cd {path}")
    os.system(f"plink --bfile 1_ancient_data/ancient_samples --distance ibs flat-missing --out 3_ibs_dist/ibs_dist")
    
    print("reading distance matrix...")
    read_dist_matrix(path)

# this function calculates the distance matrix and returns it
def calc_dist_matrix(time_bins, resolutuion):
    # get parent path
    path  = os.path.dirname(os.getcwd())
    # read in the data from the ancient samples file
    df = read_df(f'{path}/0_data/Ancient_samples.txt')
    
    print("labeling samples with time bins and hexagon ids...")
    label_samples(path, df, time_bins,resolutuion)
    
    # df = read_df(f'{path}/0_data/Ancient_samples_with_time_hexagon.txt')
    
    # print("calculating distances to neighboring hexagons...")
    # dist_matrix=calc_distance_matrix(path, df, f'{path}/3_ibs_dist/ibs_dist.mibs', f'{path}/3_ibs_dist/ibs_dist.mibs.id', resolutuion, time_bins)
    
    # return dist_matrix

# if __name__ == "__main__":
#     matrix=calc_dist_matrix(30, 2)
#     path  = os.path.dirname(os.getcwd())
#     thresholds = [0.72, 0.73, 0.74, 0.75]
#     for threshold in thresholds:
#         get_hexagons_below_threshold(path,matrix, threshold)
    
    