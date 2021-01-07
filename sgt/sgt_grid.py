import sys

import geopandas as gpd
import numpy as np
from shapely.geometry import Point


def grid(src_vector, out_vector, size):
    """ create a grid out of a shapefile and write it into another shapefile
    
    Args : 
        src_vector (str) : path to the source vector shapefile
        out_vector (str) : path to the output raster
        size (float) : the grid size in meters
        
    Return :
        out_vector
        
    """
    
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
    grid = gpd.GeoDataFrame({'geometry':points}, crs='EPSG:3857') \
        .buffer(size) \
        .envelope \
        .intersection(gdf) \
        .to_crs('EPSG:4326')
    
    # filter empty geometries
    grid = grid[np.invert(grid.is_empty)]
    
    # export as shapefile
    grid.to_file(out_vector)
    
    return out_vector

if __name__ == "__main__":
    
    # read arguments
    out_vector = sys.argv[sys.argv.index('-o') + 1]
    src_vector = sys.argv[sys.argv.index('-i') + 1]
    size = sys.argv[index('-s') + 1]
    
    # launch the function 
    res = rasterize(src_vector, out_vector, size)
    
    # dispay result 
    if res:
        print(f'The vector geometries have been transfor into grid : {out_vector}')