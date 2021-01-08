# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']
    
import unittest
from pathlib import Path

import rasterio as rio
import numpy as np

from sgt import * 

###############################
##     global parameters     ##
###############################

tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)

###############################

class TestClump(unittest.TestCase):
    
    def test_method(self):
        
        #create fake material 
        src = self.fake_tif()
        
        # clump the fake image 
        dst = tmp_dir.joinpath('result.tif')
        clump(src, dst)
        
        with rio.open(dst) as f:
            data = f.read(1)
            expected_result = self.expected_result()
            self.assetEqual(data, expected_result)
            
        return 

    def fake_tif(self):
        """create a fake tif file in EPSG:4326 center in 0,0 res 30m"""
    
        # initialte parameters 
        crs = rio.crs.CRS.from_epsg(4326)
        res = 0.00026949458523585647 # ~30m in deg
        bands, rows, cols = shape = (1, 6, 6)
        west, south, east, north = -cols*res/2, -rows*res/2, cols*res/2, rows*res/2
        transform = rio.transform.from_bounds(west, south, east, north, cols, rows)
    
        # create the dataset 
        data = np.zeros(shape, dtype=np.uint8)
        data[0, 2:4, 2:4] = 10
        data[0, 4, 4] = 10
        data[0, :2, :3] = 22
        data[0, 0, 5] = 36
    
        # burn it into a file 
        file = tmp_dir.joinpath('source.tif')
        
        kwargs = {
            'driver': 'GTiff', 
            'dtype': 'uint8', 
            'width': shape[1], 
            'height': shape[2], 
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
    
    def expected_result(self):
        
        # create the dataset 
        data = np.zeros((6,6), dtype=np.uint8)
        data[2:4, 2:4] = 1
        data[4, 4] = 1
        data[:2, :3] = 2
        data[0, 5] = 3
        
        return data