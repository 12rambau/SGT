import unittest
from pathlib import Path

import geopandas as gpd
import rasterio as rio
import numpy as np

from sgt import *

###############################
##     global parameters     ##
###############################

tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)
grid_size = 30 
nb_cell = 6

###############################

class TestRasterize(unittest.TestCase):
    
    def test_method(self):
        
        # create the fake material 
        column = 'data'
        source = self.fake_vector(column)
        res = tmp_dir.joinpath('res.tif')
        
        # rasterize the file 
        rasterize(source, res, column = column)
        
        # test the results 
        with rio.open(res) as f:
            
            data = f.read(1)
            expected_result = self.expected_result()
            
            self.assertTrue((data==expected_result).all())
            
        # delete all files 
        self.del_shp(source)
        res.unlink()
        
        return 
    
    def fake_vector(self, column):
        """create a shahpaefile composed of 1 squares, one in the middle"""
    
        gdf = gpd.GeoDataFrame({column: [1], 'geometry': [sg.Point(0,0)]}, crs='EPSG:3857') 
        gdf.geometry = gdf.geometry.buffer(nb_cell*grid_size, cap_style=3)
    
        dst = tmp_dir.joinpath('shapes.shp')
    
        gdf.to_file(dst)
    
        return dst
    
    def del_shp(self, file):
        "remove a shapefile and all the related file in the process"
        
        pattern = f'{file.stem}.*'
        file_list = tmp_dir.glob(pattern)
        
        for file in file_list:
            file.unlink()
        
        return
    
    def expected_result(self):
        
        res = np.ones((12,12), dtype=np.uint8)
        
        return res