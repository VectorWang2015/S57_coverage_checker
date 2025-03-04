import os
import os.path
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import argparse

from typing import Tuple
from shapely.ops import unary_union

from welzl import welzl

config_path = "./config.json"

parser = argparse.ArgumentParser()
parser.add_argument("--output", "-o", type=str, required=True)

def get_s57_file_coverage(file_name: str, debug=False) -> Tuple[Tuple[float, float], float]:
    """
    input:
        file path for s-57 file
    calcul:
        minimum coverage circle for this particular s-57 ENC
    return:
        ((longi, lati), radius)
        unit: degrees
    """
    # read file and find convex hull for coverage area
    gdf = gpd.read_file(file_name, layer="M_COVR")
    union_geom = unary_union(gdf.geometry)
    convex_hull = union_geom.convex_hull
    convex_hull_coords = list(convex_hull.exterior.coords)

    # find min circle using welzl
    min_circle = welzl(convex_hull_coords)

    # visualize for debug use
    if debug == True:
        fig, ax = plt.subplots()
        circle = plt.Circle((min_circle[0], min_circle[1]), min_circle[2])
        ax.add_patch(circle)
        gpd.GeoSeries(convex_hull).plot(ax=ax, edgecolor='red', facecolor='none')
        plt.show()

    return min_circle

if __name__ == "__main__":
    args = parser.parse_args()
    output_path = args.output

    coverage_data = {}

    # fetch paths for all s57 files within source directory
    with open(config_path, "r") as fd:
        s57_source = json.load(fd)["s57_dir"]

    s57_file_paths = os.listdir(s57_source)
    s57_ids = [file_name[:-4] for file_name in s57_file_paths if file_name[-4:] == ".000"]
    s57_file_paths = [os.path.join(s57_source, file_name) for file_name in s57_file_paths]

    for s57_id, file_name in zip(s57_ids, s57_file_paths):
        min_circle = get_s57_file_coverage(file_name)
        coverage_data[s57_id] = min_circle
    
    print("Writing parsed s-57 coverage data to: {}".format(output_path))
    with open(output_path, "w") as fd:
        fd.write(json.dumps(coverage_data))