# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']
    
import unittest
from pathlib import Path
import numpy as np

from sgt import *

###############################
##     global parameters     ##
###############################

tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)

###############################

@unittest.skip("not functional as I don't know the expected result")
class TestAlign(unittest.TestCase):
    
    def test_method(self):
        
        # create fake material 
        source = self.fake_source()
        template = self.fake_template()
        res = tmp_dir.joinpath('res.tif')
        
        # alig source to the template 
        sgt.align(source, template, res)
        
        # expected result : 
        # TODO find what is the expected result
        expected_result = np.ones((1,60,60), dtype=np.uint8)
        
        with rio.open(res) as res_f, rio.open(template) as template_f:
            self.assertEqual(res_f.crs, template.crs)
            self.assertEqual(res_f.bounds, template.bounds)
            self.assertEqual(res_f.read(), expected_result)
        
        return
    
    def fake_source(self):
        """create a fake tif of defined shap with only 1s in EPSG:4326 with landsat res (30m)"""
    
        # initiate parameters 
        crs = rio.crs.CRS.from_epsg(4326)
        res = 0.00026949458523585647 # ~30m in deg
        bands, rows, cols = shape = (1, 60, 60)
        west, south, east, north = -cols*res/2, -rows*res/2, cols*res/2, rows*res/2
        transform = rio.transform.from_bounds(west, south, east, north, cols, rows)
    
        # create a dataset 
        data = np.ones(shape, dtype=np.uint8)*255
        data = np.triu(data)
        
        # burn it into a file 
        file = tmp_dir.joinpath('source.tif')
        
        kwargs = {
            'driver': 'GTiff', 
            'dtype': 'uint8', 
            'width': shape[1], 
            'height': shape[2], 
            'nodata': 0,
            'count': bands, 
            'crs': crs, 
            'tiled': False, 
            'compress': 'lzw', 
            'interleave': 'band',
            'transform': transform
        }
        
        with rio.open(file, 'w', **kwargs) as dst:
            dst.write(data)
        
        return file

    def fake_template(self):
        """create a fake tif template of defined shape with only 1s in mertcator utm with sentinel res (10m)"""
        
        # initiate parameters 
        crs = rio.crs.CRS.from_epsg(3857)
        res = 10 # ~10m in deg
        bands, rows, cols = shape = (1, 300, 300)
        west, south, east, north = -cols*res/2, -rows*res/2, cols*res/2, rows*res/2
        transform = rio.transform.from_bounds(west, south, east, north, cols, rows)
        
        # create a dataset 
        data = np.ones(shape, dtype=np.uint8)*255
            
        # burn it into a file 
        file = tmp_dir.joinpath('template.tif')
            
        kwargs = {
            'driver': 'GTiff', 
            'dtype': 'uint8', 
            'width': shape[1], 
            'height': shape[2], 
            'nodata': 0,
            'count': bands, 
            'crs': crs, 
            'tiled': False, 
            'compress': 'lzw', 
            'interleave': 'band',
            'transform': transform
        }
            
        with rio.open(file, 'w', **kwargs) as dst:
            dst.write(data)
            
        return file
    