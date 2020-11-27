import sys

import rasterio as rio

def align(src_rst, template_rst, out_rst):
    """ Align a source raster on a template
    
    Args : 
        src_rst (str) : path to the source raster
        template_rst (str) : path to the template raster
        out_rst (str) : path to the output raster
        
    Return :
        out_rst
        
    """
    
    # get template crs and transform 
    with rio.open(template_rst) as tplt, rio.open(src_rst) as src:      
        
        kwargs = src.meta.copy()
        
        kwargs.update(
            driver = 'GTiff',
            height = tplt.height,
            width = tplt.width,
            transform = tplt.transform,
            compress='lzw'
        )
        
        #destination
        with rasterio.open(out_rst, 'w', **kwargs) as dst:
            for i in range(1, dst.count+1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=tplt.transform,
                    dst_crs=tplt.crs,
                    resampling=Resampling.bilinear
                ) 
    return

if __name__ == "__main__":
    
    # read arguments
    out_rst = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    template_rst = sys.argv[sys.argv.index('-t') + 1]
    
    # launch the function 
    res = align(src_rst, template_rst, out_rst)