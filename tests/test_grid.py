# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']
    
import unittest
from pathlib import Path

import geopandas as gpd
import numpy as np

from sgt import *

###############################
##     global parameters     ##
###############################

grid_size = 30 #(meter)
nb_cell = 6 # number of grid cells in the starting element
tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)

###############################

class TestGrid(unittest.TestCase):
    
    def test_method(self):
        
        # create fake material 
        src = self.fake_shape()
        
        # create the grid 
        dst = tmp_dir.joinpath('result.shp')
        grid(src, dst, grid_size)
        
        # check the grid 
        res = gpd.read_file(dst)
        
        self.assertEqual(len(res), 144)
        
        bounds = np.ndarray([-0.00161697, -0.00161697,  0.00161697,  0.00161697])
        self.assertTrue((res.total_bounds==bounds).all())
        
        # delete all files 
        self.del_shp(src)
        self.del_shp(dst)
        
        return 
    
    def fake_shape():
        """create a shahpaefile composed of 1 squares, one in the middle"""
    
        gdf = gpd.GeoDataFrame({'geometry': [sg.Point(0,0)]}, crs='EPSG:3857') .buffer(nb_cell*grid_size, cap_style=3)
    
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