from adjust_sample_lists import split_ancient_modern
from label_samples_time_hexa import label_samples, read_df
from calc_distances import calc_distances
import os

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
    os.system(f"plink --bfile 1_ancient_data/ancient_samples --distance ibs flat-missing --out 3_ibs_dist/ibs_dist")

    
def run(time_bins, resolutuion, threshold):
    path = os.getcwd()
    # read in the data from the ancient samples file
    df = read_df(f'{path}/0_data/Ancient_samples.txt')
    
    print("labeling samples with time bins and hexagon ids...")
    label_samples(path, df, time_bins,resolutuion)
    
    df = read_df(f'{path}/0_data/Ancient_samples_with_time_hexagon.txt')
    
    print("calculating distances to neighboring hexagons...")
    neighbor_dist_time_bin=calc_distances(path, df, f'{path}/3_ibs_dist/ibs_dist.mibs', f'{path}/3_ibs_dist/ibs_dist.mibs.id',threshold, resolutuion, time_bins)

if __name__ == "__main__":
    run(30, 2, 0.72)
    
    