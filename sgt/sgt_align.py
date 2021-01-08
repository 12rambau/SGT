# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']

import sys
import pathlib

import rasterio as rio
from rasterio import warp

from sgt.utils import custom_print

def align(src_rst, template_rst, out_rst, verbose=False):
    """ Align a source raster on a template
    
    Args : 
        src_rst (str) : path to the source raster
        template_rst (str) : path to the template raster
        out_rst (str) : path to the output raster
        
    Return :
        out_rst
        
    """
    
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # get template crs and transform 
    with rio.open(template_rst) as tplt, rio.open(src_rst) as src:
        
        transform, width, height = warp.calculate_default_transform(
            src.crs, 
            tplt.crs, 
            tplt.width, 
            tplt.height, 
            *tplt.bounds
        )
        
        kwargs = src.meta.copy()
        
        kwargs.update(
            driver    = 'GTiff',
            height    = height,
            width     = width,
            transform = transform,
            compress  = 'lzw'
        )
        
        #destination
        with rio.open(out_rst, 'w', **kwargs) as dst:
            for i in range(1, dst.count+1):
                warp.reproject(
                    source        = rio.band(src, i),
                    destination   = rio.band(dst, i),
                    src_transform = src.transform,
                    src_crs       = src.crs,
                    dst_transform = transform,
                    dst_crs       = tplt.crs,
                    resampling    = warp.Resampling.bilinear
                )
                
    v_print(f'The raster {src_rst} has been align on {template_rst} in {out_rst}')
                
    return

if __name__ == "__main__":
    
    import argparse
    
     # write the description 
    descript = "Align a source raster on a template"
    
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
        metavar = 'out.tif',
        help = '(str) : path to the output raster',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-t',
        dest = 'template_rst',
        metavar = 'template.tif',
        help = '(str) : path to the template raster',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '--no-v',
        dest = 'verbose',
        action='store_false',
        required = False,
        help = "remove the verbose option"
    )
    
    # parse tha current arguments
    args = parser.parse_args()
    
    # launch the function 
    align(**vars(args))
        