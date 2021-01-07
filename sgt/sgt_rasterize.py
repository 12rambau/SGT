import sys

import rasterio as rio
import numpy as np
import geopandas as gpd

default_profile = {
    'driver': 'GTiff', 
    'dtype': 'float64', 
    'nodata': np.nan, 
    'width': 2000, 
    'height': 2000, 
    'count': 1, 
    'crs': rio.crs.CRS.from_epsg(4236), 
    'tiled': False, 
    'compress': 'lzw', 
    'interleave': 'band'
}

def rasterize(src_vector, out_rst, res=30, column=None):
    """ Burns vector geometries into a raster.
    
    Args : 
        src_vector (str) : path to the source vector shapefile
        out_rst (str, optional) : path to the output raster
        res (int, optional) : the resolution of the output raster. If none, the default landsat 7 30m res will be used
        column (str, optional) : the name of the column to use as value in the output raster. use the first one if none
        
    Return :
        out_rst
        
    """
    
    # read the vector data
    gdf = gpd.read_file(src_vector).to_crs("EPSG:4326")
    
    # identify the column to be burn in the raster 
    if not column:
        column = gdf.columns[0]
        
    # create the (geometry, value) tuples
    shapes = []
    for index, row in gdf.iterrows():
        shapes.append(row.geometry, row[column])
        
    # convert the metric resolution into deg (as we work in EPSG 4326)
    # consider the equator approximation : 1° = 111 Km
    res = (res/111)*(10**(-3))
        
    # define the shape based on the required resolution
    minx, miny, maxx, maxy = df.geometry.total_bounds
    width = int((maxx-minx)/res)
    height = int((maxy-miny)/res)
    
    # burn the result in the output data array
    data = rio.features.rasterize(shapes, out_shape=(height, width), all_touched=True)
    
    
    out_meta = default_profile
    out_met.update(
        width = width,
        height = height,
        dtype = rio.dtypes.get_minimum_dtype(data)
    )
    
    with rio.open(out_rst, 'w', **out_meta) as dst:
        data = data.astype(dst.profile['dtype'])
        dst.write(data)
        
    return out_rst

if __name__ == "__main__":
    
    # read arguments
    out_rst = sys.argv[sys.argv.index('-o') + 1]
    src_vector = sys.argv[sys.argv.index('-i') + 1]
    column = sys.argv[index('-col') + 1]
    
    # launch the function 
    res = rasterize(src_vector, out_rst, column)
    
    # dispay result 
    if res:
        print(f'The vector geometries have been burn into the raster : {out_rst}')