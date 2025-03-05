import os
import os.path
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from typing import Tuple, Iterable
from shapely.ops import unary_union
from shapely import Polygon

config_path = "./config.json"
coverage_path = "./coverage.json"


def find_s57_within_range(
        longi: float,
        lati: float,
        size: float,
        debug: bool=False,
) -> Iterable[str]:
    s57_candidates = []

    with open(coverage_path, "r") as fd:
        s57_dict = json.loads(fd.read())
    
    os_r = size * np.sqrt(2)

    for s57_id in s57_dict.keys():
        area_longi, area_lati, r = s57_dict[s57_id]

        dist = np.hypot(longi-area_longi, lati-area_lati)
        if dist <= (os_r + r):
            s57_candidates.append(s57_id)
    return s57_candidates



def find_s57_within_range_native(
        longi: float,
        lati: float,
        size: float,
        debug: bool=False,
) -> Iterable[str]:
    if debug:
        fig, ax = plt.subplots()

    s57_candidates = []
    # create shape for OS coverage
    os_coverage = Polygon(
        [
            (longi+size, lati+size), (longi-size, lati+size),
            (longi-size, lati-size), (longi+size, lati-size),
        ]
    )

    if debug:
        gpd.GeoSeries(os_coverage).plot(ax=ax, edgecolor='red', facecolor='none')

    # fetch paths for all s57 files within source directory
    with open(config_path, "r") as fd:
        s57_source = json.load(fd)["s57_dir"]

    s57_file_paths = os.listdir(s57_source)
    s57_ids = [file_name[:-4] for file_name in s57_file_paths if file_name[-4:] == ".000"]
    s57_file_paths = [os.path.join(s57_source, file_name) for file_name in s57_file_paths]

    for s57_id, file_name in zip(s57_ids, s57_file_paths):
        gdf = gpd.read_file(file_name, layer="M_COVR")
        union_geom = unary_union(gdf.geometry)
        convex_hull = union_geom.convex_hull

        if convex_hull.intersects(os_coverage):
            s57_candidates.append(s57_id)
            if debug:
                gpd.GeoSeries(convex_hull).plot(ax=ax, edgecolor='blue', facecolor='none')

    if debug:
        plt.show()
    return s57_candidates


if __name__ == "__main__":
    s57_candidates = find_s57_within_range_native(
        longi=120.25, lati=36, size=0.5
    )
    print(s57_candidates)
    s57_candidates_2 = find_s57_within_range(
        longi=120.25, lati=36, size=0.5
    )
    print(s57_candidates_2)
    
    for candidate in s57_candidates:
        assert candidate in s57_candidates_2