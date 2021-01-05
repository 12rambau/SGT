import sys

import rasterio as rio
import pandas as pd

def addpct(src_rst, colors, out_rst=None):
    """ Align a source raster on a template
    
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
    
    return out_rst

if __name__ == "__main__":
    
    # read arguments
    out_rst = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    colors = sys.argv[sys.argv.index('-c') + 1]
    
    # launch the function 
    res = addpct(src_rst, colors, out_rst)
    
    # dispay result 
    if res:
        print(f'The color palette have been add to the raster and saved in {out_rst}')