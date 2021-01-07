import sys

import rasterio as rio
import pandas as pd


def add_pct(src_rst, colors, out_rst=None):
    """ Add a palette color table to the first band of a raster image
    
    Args : 
        src_rst (str) : path to the source raster
        colors (str) : path to the color table
        out_rst (str, optional) : path to the output raster, will overwrite the input file if None
        
    Return :
        out_rst
        
    """
    
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
    with rasterio.open(src_rst) as src:
        out_meta = src.meta.copy()
        
    with rasterio.open(out_rst, "w", **out_meta) as dst:
        dst.write_colormap(1, colormap)
        
    #print(f'The color palette have been add to the raster and saved in {out_rst}')
    
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
        '--src_rst',
        metavar = 'source.tif',
        help = '(str) : path to the source raster',
        required = True
    )
    parser.add_argument(
        '-c',
        '--colors',
        metavar= 'color_table.csv',
        help = '(str) : path to the color table',
        required = True
    )
    parser.add_argument(
        '-o',
        '--out_rst',
        metavar = 'output.tif',
        help = '(str) : path to the output raster',
        required = False
    )
    
    args = parser.parse_args()
    
    print(args.burst_inventory)
    print(args.config_file)
    
    # launch the function 
    add_pct(**vars(args))