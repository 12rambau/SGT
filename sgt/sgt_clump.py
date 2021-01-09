import sys
import pathlib
import argparse

import rasterio as rio
from scipy import ndimage as ndi
import numpy as np

from sgt.utils import custom_print

def clump(src_rst, out_rst, band=1, mask_rst=None, verbose=False):
    """ Add spatial coherency to existing classes by combining
adjacent similar classified areas.
    
    Args : 
        src_rst (str) : path to the source raster
        out_rst (str) : path to the output raster
        band (int, optionnal) : use determined band of the image (if not defaulted to the first one)
        mask_rst (str, optional) : use maskfile and process only areas having mask
value >0
        verbose (bool) : wether to display the print info
        
    Return :
        out_rst
        
    """
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # default to 8 neigbours
    struct = ndi.generate_binary_structure(2,2)

    with rio.open(src_rst) as src:
        
        raster = src.read(band)
        meta = src.meta.copy()
        
    # mask raster if needed 
    if mask_rst:
        with rio.open(mask_rst) as src:
            mask = src.read(1)
            
            raster = (mask != 0) * raster
            
    # adapt the raster size to optimize memory usage 
    dtype = rio.dtypes.get_minimum_dtype(raster)
    raster = raster.astype(dtype)
    
    # the raster can be non-binary each value need to be clump separately
    
    # identify the features 
    count = np.bincount(raster.flatten())
    features = np.where(count!=0)[0]
    
    del count
    
    # init 
    offset = 0
    raster_labeled = np.zeros(raster.shape, dtype=raster.dtype)
    
    # loop in values
    for feature in features[1:]: 
        
        # label the filtered dataset
        label = ndi.label(raster == feature, structure = struct)[0]
        label[label!=0] = offset + label[label!=0] 
        
        # add it to the dataset
        raster_labeled = raster_labeled.astype(label.dtype)
        raster_labeled += label     
        
        # increase coef
        offset = np.amax(raster_labeled)
        
    # free memory
    del raster
        
    # adapt the raster size to optimize memory usage 
    dtype = rio.dtypes.get_minimum_dtype(raster_labeled)
    raster_labeled = raster_labeled.astype(dtype)
    meta.update(dtype = dtype)
    
    with rio.open(out_rst, 'w', **meta) as dst:
        dst.write(raster_labeled, 1)
            
    del raster_labeled
        
    v_print(f'The raster has been clumped in {out_rst}')
    
    return

if __name__ == "__main__":
    
    # write the description 
    descript = "Add spatial coherency to existing classes by combining adjacent similar classified areas."
    
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
        '-b',
        dest = 'band',
        metavar = 'band_index',
        help = '(int) : use determined band of the image (if not defaulted to the first one)',
        required = False,
        type = int
    )
    parser.add_argument(
        '-um',
        dest = 'mask_rst',
        metavar = 'mask.tif',
        help = '(str) : use maskfile and process only areas having mask value >0',
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
    
    # read arguments
    args = parser.parse_args()
    
    # launch the function 
    res = clump(**vars(args))