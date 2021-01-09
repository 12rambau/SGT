# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']
    
import unittest 
from pathlib import Path

import rasterio as rio 
import numpy as np 
import geopandas as gpd
import shapely.geometry as sg

from sgt import *

###############################
##     global parameters     ##
###############################

tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)

# initialte parameters 
crs = rio.crs.CRS.from_epsg(4326)
res = 0.00026949458523585647 # ~30m in deg
bands, rows, cols = shape = (1, 6, 6)
west, south, east, north = -cols*res/2, -rows*res/2, cols*res/2, rows*res/2

###############################

class TestCutline(unittest.TestCase):
    
    def test_method(self):
        
        # create fake material 
        src = self.fake_tif()
        shapes = self.fake_shapes()
        
        # cut the image to the shape 
        dst = tmp_dir.joinpath('result.tif')
        cutline(src, shapes, dst)
        
        with rio.open(dst) as f:
            data = f.read(1)
            expected_result = self.expected_result()
            self.assertTrue((data==expected_result).all())
            
        # delete all files
        os.remove(src)
        os.remove(shapes)
        os.remove(dst)
        
        return 
    
    def fake_tif(self):
        """create a fake tif file in EPSG:4326 center in 0,0 res 30m"""
        
        # create the transform from bounds of the image
        transform = rio.transform.from_bounds(west, south, east, north, cols, rows)
    
        # create the dataset 
        data = np.ones((6,6), dtype=np.uint8)
    
        # burn it into a file 
        file = tmp_dir.joinpath('source.tif')
        
        kwargs = {
            'driver': 'GTiff', 
            'dtype': 'uint8', 
            'width': shape[1], 
            'height': shape[2], 
            'count': 1, 
            'nodata': 0,
            'crs': crs, 
            'tiled': False, 
            'compress': 'lzw', 
            'interleave': 'band',
            'transform': transform
        }
        
        with rio.open(file, 'w', **kwargs) as dst:
            dst.write(data, 1)
        
        return file

    def fake_shape():
        """create a shahpaefile composed of 2 squares, one in the middle and one in the top left corner"""
        
        gdf = gpd.GeoDataFrame({'geometry': [sg.Point(0,0), sg.Point(west, north)]}, crs=crs) \
            .to_crs('EPSG:3857') \
            .buffer(5, cap_style=3)
    
        file = tmp_dir.joinpath('shapes.shp')
    
        gdf.to_file(file)
    
        return file  
    
    def expected_result(self):
        
        # create the dataset
        data = np.zeros((4,4), dtype=np.uint8)
        data[1,1] = 1
        data[2:,2:] = 1
        
        return data
    