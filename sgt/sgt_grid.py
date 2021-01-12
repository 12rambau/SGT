import sys
import pathlib
import argparse
from itertools import product

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from sgt.utils import custom_print

def grid(src_vector, out_vector, size, verbose=False):
    """ create a grid out of a shapefile and write it into another shapefile
    
    Args : 
        src_vector (str) : path to the source vector shapefile
        out_vector (str) : path to the output vector file
        size (float) : the grid size in meters        
    """
    
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # read the vector data in mercator proj
    gdf = gpd.read_file(src_vector).to_crs('EPSG:3857')
    
    # extract bounds from gdf 
    min_lon, min_lat, max_lon, max_lat = gdf.total_bounds
    
    # compute the longitudes and latitudes top left corner coordinates
    longitudes = np.arange(min_lon, max_lon, size)
    latitudes = np.arange(min_lat, max_lat, size)
    
    # create the grid geometry
    points = []
    for coords in product(longitudes, latitudes):
        points.append(Point(coords[0], coords[1]))

    # create a buffer grid in lat-long
    grid = gpd.GeoDataFrame({'geometry':points}, crs='EPSG:3857').buffer(size, cap_style=3)
    grid = gpd.clip(grid, gdf)
    grid = grid.to_crs('EPSG:4326')
    
    # export as shapefile
    grid.to_file(out_vector)
    
    v_print(f'The vector geometries have been transfor into grid : {out_vector}')
    
    return out_vector

if __name__ == "__main__":
    
    # write the description 
    descript = "create a grid out of a shapefile and write it into another shapefile"
    
    # create an arg parser
    parser = argparse.ArgumentParser(description=descript)
    
    # read arguments 
    parser.add_argument(
        '-i',
        dest = 'src_vector',
        metavar = 'source.shp',
        help = '(str) : path to the source vector file',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-o',
        dest = 'out_vector',
        metavar = 'output.shp',
        help = '(str) : path to the output vector file',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-s',
        dest = 'size',
        metavar = 'a_number',
        help = '(int) : the grid size in meters',
        required = True,
        type = int
    )
    parser.add_argument(
        '--no-v',
        dest = 'verbose',
        action='store_false',
        required = False,
        help = "remove the verbose option"
    )  
    
    # read arguments
    args = parser.parse_args()
    
    # launch the function 
    grid(**vars(args))