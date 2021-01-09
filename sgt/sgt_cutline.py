import sys
import pathlib 
import argparse

import rasterio as rio
from rasterio.mask import mask
import geopandas as gpd

from sgt.utils import custom_print

def cutline(src_rst, shape_vector, out_rst, verbose=False):
    """ Cut the raster on a .shp vector file
    
    Args : 
        src_rst (str) : path to the source raster
        shape_vector (str) : path to the cutting shapefile
        out_rst (str) : path to the output raster
        verbose (bool) : wether to display the print info
        
    Return :
        out_rst
        
    """
    
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # cut the source raster 
    with rio.open(src_rst) as src:
        
        # get the crs 
        crs = src.crs
        
        # read the shapefile 
        gdf = gpd.read_file(shape_vector).to_crs(crs)
        shapes = gdf.geometry
    
        out_image, out_transform = mask(src, shapes, all_touched=True, crop=True)
    
        out_meta = src.meta.copy()
        out_meta.update(
            driver = 'GTiff',
            height = out_image.shape[1],
            width = out_image.shape[2],
            transform = out_transform,
            compress='lzw'
        )
    
    # write the croped image into the dst file
    with rio.open(out_rst, "w", **out_meta) as dst:
        dst.write(out_image)
    
    v_print(f'The raster has been cut to {shape_vector} extends and saved in {out_rst}')
    
    return

if __name__ == "__main__":
    
    # write the description
    descript = "Cut the raster on a .shp vector file"
    
    # create an arg parser 
    parser = argparse.ArgumentParser(description=descript)
    
    # read arguments
    parser.add_argument(
        '-i',
        dest = 'src_rst',
        metavar = 'source.tif',
        help = '(str) : path to the source raster',
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
        '-s',
        dest = 'shape_vector',
        metavar = 'shapes.shp',
        help = '(str) : path to the vector file',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '--no-v',
        dest = 'verbose',
        action='store_false',
        required = False,
        help = 'remove the verbose option'
    )  
    
    # read arguments
    args = parser.parse_args()
    
    # launch the function 
    cutline(**vars(args))
        