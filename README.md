# GeoGeneTrack

## Introduction

GeoGenTrack is a bioinformatics tool designed to explore the relationship between genetic and geographical distances using ancient DNA data. It employs the AADR dataset, which consists of approximately 10,000 ancient DNA samples analyzed across 1,233,013 genomic sites. The tool identifies areas where the expected correlation between geographical and genetic distances does not hold by organizing data into geographic hexagons and time bins, which can be customized by the user. It calculates the average Identity by State (IBS) among neighboring hexagons and visualizes this data on a map, allow the identification of violations in the genetic-geographic distance correlation. GeoGenTrack offers features like customizable precision searching, efficient violation identification, and extended neighbor analysis, making it a valuable resource for researchers interested in the dynamics of genetic diversity and population movements over time. The tool's efficiency, however, is limited by the explanatory power of IBS for genetic distances.

## Setup

### Conda env

To ensure that the project's dependencies do not conflict with those of other projects, we create a new Conda environment, and load it whit all dependencies that are needed for the application by setting geogentrack.yml as the file parameter.

```{bash}
conda env create --name geogentrack --file==envs/geogentrack.yml
```

### How to get the IBS matrix

Before you can use the application, it's crucial to have the Identity by State (IBS) matrix prepared. To obtain the necessary IBS matrix for the software, there are two distinct methods available.

#### Download the ibs_dist.mibs.pkl

The simplest method to acquire the IBS matrix is by downloading it from the provided link. After downloading, the matrix must be placed in the 3_ibs_dist/ directory located within the GeoGenTrack directory.
link: <https://drive.google.com/drive/u/3/folders/1mh_AfML7DDK2JIpAkX7jHlWRADjI1Z1Z>

IMPORTANT:
Do not rename the file.
This is how the relative path of the file should look like: 3_ibs_dist/ibs_dist.mibs.pkl

#### Create the ibs_dist.mibs.pkl

The second way, is to create the file yourself. For that the python script initial_run.py has to be run. For this to work the script needs a directory called 0_data/ which has to include the following files

- AADR Annotation.xlsx
- samples.bed
- samples.fam
- samples.bim

Once assured that the files are in the 0_data/ directory run the initial_run python script.

```{bash}
python scr/initial_run.yp
```

### Before running

1) make sure that you created and activated the conda environment with the given yml file

2) make sure that your working directory contains the following files:

    - 0_data/Ancient_samples.txt
    - 3_ibs_dist/ibs_dist.mibs.pkl

## Usage

Now the interactive GeoGenTrack can be started with the following bash command.

```{bash}
streamlit run scr/app.py
```

This should automatically open a browser window with the GeoGEnTrack application.

## Explanation of the workflow

- The interface enables users to customize the number of time divisions and the resolution of the hexagonal areas, with more information available on the UI's homepage.
- The feature "Expand search area" allows the application to scout for adjacent hexagonal areas at increased distances.
- Upon activation, GeoGenTrack categorizes the ancient samples according to the selected time bins and hexagonal dimensions based on the specified resolution.
- The UI presents a map displaying all hexagons containing samples from the latest time bin, along with their mean Identity by State (IBS) values in relation to neighboring hexagons.
- Users now have the capability to look at all different time bins, standardize the mean IBS values, apply filters based on set thresholds,or explore the interactive map.

## Contact Information

If there are any problems with the application please contact: <ja2332st-s@student.lu.se>
