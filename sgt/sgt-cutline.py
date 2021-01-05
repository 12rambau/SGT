import sys

import rasterio as rio
import geopandas as gpd

def cutline(src_rst, shape_vector, out_rst):
    """ Align a source raster on a template
    
    Args : 
        src_rst (str) : path to the source raster
        shape_vector (str) : path to the cutting shapefile
        out_rst (str) : path to the output raster
        
    Return :
        out_rst
        
    """
    
    # read the shapefile 
    gdf = gpd.read_file(shape_vector)
    shapes = gdf.geometry
    
    # cut the source raster 
    with rasterio.open(src_rst) as src:
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
    with rasterio.open(out_rst, "w", **out_meta) as dst:
        dst.write(out_image)
    
    return out_rst

if __name__ == "__main__":
    
    # read arguments
    out_rst = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    shape_vector = sys.argv[sys.argv.index('-s') + 1]
    
    # launch the function 
    res = cutline(src_rst, shape_vector, out_rst)
    
    # dispay result 
    if res:
        print(f'The raster has been cut to {shape_vector} extends and saved in {out_rst}')