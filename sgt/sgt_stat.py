import sys

import rasterio as rio
import numpy as np

def his(src_rst, out_csv, mask_vector):
    """ computes image histogram by segments. 
    
    Args : 
        src_rst (str) : path to the source raster
        out_csv (str) : path to the output csv file
        mask_rst (str, optional) : path to the mask raster (a labeled raster 0 being the background)
        
    Return :
        out_csv
    """

    
    return df

if __name__ == "__main__":
    
    # read arguments
    out_csv = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    mask_vector = sys.argv[index('-s') + 1]
    
    # launch the function 
    res = his(src_rst, out_csv, mask_rst)
    
    # dispay result 
    if res:
        print(f'The zonal analysis have been created : {out_csv}')