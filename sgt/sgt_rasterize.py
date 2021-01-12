import sys
import pathlib
import argparse

import geopandas as gpd
from geocube.api.core import make_geocube
import rasterio as rio
import numpy as np

from sgt.utils import custom_print

def rasterize(src_vector, out_rst, res=30, column=None, verbose=False):
    """ Burns vector geometries into a raster.
    
    Args : 
        src_vector (str) : path to the source vector shapefile
        out_rst (str, optional) : path to the output raster
        res (int, optional) : the resolution of the output raster. If none, the default landsat 7 30m res will be used
        column (str, optional) : the name of the column to use as value in the output raster. default ot the first one        
    """
    
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # read the vector data
    gdf = gpd.read_file(src_vector).to_crs("EPSG:4326")
    
    # identify the column to be burn in the raster 
    if not column:
        column = gdf.columns[0]
        
    # optimize dtype 
    dtype = rio.dtypes.get_minimum_dtype(gdf[column])
    
    # optimize the nodata value to meet the dtype
    fill = np.nan
    if np.issubdtype(dtype, np.integer):
        fill = 0
        
    # convert the metric resolution into deg (as we work in EPSG 4326)
    # consider the equator approximation : 1° = 111 Km
    res = (res/111)*(10**(-3))

    out_grid = make_geocube(
        vector_data = gdf,
        measurements = [column],
        resolution = (-res, res),
        fill = fill
    )

    # write the column to raster file
    out_grid[column].rio.to_raster(out_rst, dtype=dtype)
    
        
    v_print(f'The vector geometries have been burn into the raster : {out_rst}')
        
    return

if __name__ == "__main__":
    
    #write the description 
    descript = "Burns vector geometries into a raster"
    
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
        dest = 'out_rst',
        metavar = 'output.tif',
        help = '(str) : path to the output raster',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-res',
        dest = 'res',
        metavar = 'a_number',
        help = '(int) : the resolution of the output raster. If none, the default landsat 7 30m res will be used',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-c',
        dest = 'column',
        metavar = 'a_name',
        help = '(str) : the name of the column to use as value in the output raster. default ot the first one  ',
        required = False,
        type = str
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
    rasterize(**vars(args))