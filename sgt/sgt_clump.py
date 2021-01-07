import sys

import rasterio as rio
from scipy import ndimage as ndi

def clump(src_rst, out_rst, band=1, mask_rst=None):
    """ Add spatial coherency to existing classes by combining
adjacent similar classified areas.
    
    Args : 
        src_rst (str) : path to the source raster
        band (int) : use determined band of the image
        out_rst (str) : path to the output raster
        mask_rst (str) : use maskfile and process only areas having mask
value >0
        
    Return :
        out_rst
        
    """
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
            
    #adapt the raster size to optimize memory usage 
    dtype = rio.dtypes.get_minimum_dtype(raster)
    raster = raster.astype(dtype)
        
    # label the raster
    raster_labeled = ndi.label(raster, structure = struct)[0]
    
    # free the memory occupied by the raster 
    del raster
    
    # change the dtype of the destination file
    dtype = rio.dtypes.get_minimum_dtype(raster_labeled)
    raster_labeled = raster_labeled.astype(dtype)
    meta.update(dtype = dtype)
                         
    # write the file in the output raster
    with rio.open(out_rst, 'w', **meta) as dst:
        dst.write(raster_labeled, 1)
    
    return out_rst

if __name__ == "__main__":
    
    # read arguments
    out_rst = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    band = sys.argv[sys.argv.index('-b') + 1]
    mask_rst = sys.argv[sys.argv.index('-um') + 1]
    
    # launch the function 
    res = clump(src_rst, out_rst, band, mask_rst)
    
    # dispay result 
    if res:
        print(f'The raster has been clumped in {res}')