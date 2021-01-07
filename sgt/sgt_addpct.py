import sys
import logging
import pathlib

import rasterio as rio
import pandas as pd

from sgt.utils import custom_print

def add_pct(src_rst, colors, out_rst=None, verbose=False):
    """ Add a palette color table to the first band of a raster image
    
    Args : 
        src_rst (str) : path to the source raster (need to be in bytes (unint8))
        colors (str) : path to the color table
        out_rst (str, optional) : path to the output raster, will overwrite the input file if None
        verbose (bool, optional) : "wether the function must output information or not"
        
    Return :
        out_rst
        
    """
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # read the colors palette 
    header = ['value', 'red', 'green', 'blue', 'alpha']
    df = pd.read_csv(colors, names= header).fillna(255,  downcast='infer')
    
    # transform the df into a dictionnary compatible with rasterio
    colormap = {}
    for index, row in df.iterrows():
        colormap[row.value] = (row.red, row.green, row.blue, row.alpha)
    
    # select output file 
    if not out_rst: 
        out_rst = src_rst
        
    # add the pct to the output file 
    with rio.open(src_rst) as src:
        out_meta = src.meta.copy()
        data = src.read()
        
    with rio.open(out_rst, "w", **out_meta) as dst:
        dst.write(data)
        dst.write_colormap(1, colormap)
        
    v_print(f'The palette color table has been added to {out_rst}')
    
    return

if __name__ == "__main__":
    
    import argparse
    
    # write the description 
    descript = "Add a palette color table to the first band of a raster image"
    
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
        '-c',
        dest = 'colors',
        metavar= 'color_table.csv',
        help = '(str) : path to the color table',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-o',
        dest = 'out_rst',
        metavar = 'output.tif',
        help = '(str) : path to the output raster',
        required = False,
        type = pathlib.Path
    )
    
    parser.add_argument(
        '--no-v',
        dest = 'verbose',
        action='store_false',
        required = False,
        help = "remove the verbose option"
    )
    
    #parse tha current arguments
    args = parser.parse_args()
    
    # launch the function 
    add_pct(**vars(args))