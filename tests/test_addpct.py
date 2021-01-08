# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']

import unittest
from pathlib import Path

import numpy as np 
import rasterio as rio 
import pandas as pd

from sgt import *

###############################
##     global parameters     ##
###############################

color_1 = (0, 0, 255, 255)
color_2 = (0, 255, 0, 255)
tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)

###############################

#@unittest.skip('because')
class TestAddPCT(unittest.TestCase):
    
    def test_method(self):
        
        # create a fake material
        src = self.fake_tif()
        table = self.fake_table()
        
        # add the color palette to another file 
        dst = tmp_dir.joinpath('result.tif')
        add_pct(src, table, dst)
        
        # check the colors of dst file 
        with rio.open(dst) as f:
            self.assertEqual(color_1, f.colormap(1)[0])
            self.assertEqual(color_2, f.colormap(1)[1])
        
        # add the palette to the current file 
        add_pct(src, table)
        
        #check the colors of src file 
        with rio.open(src) as f:
            self.assertEqual(color_1, f.colormap(1)[0])
            self.assertEqual(color_2, f.colormap(1)[1])
        
        # delete everything
        os.remove(src)
        os.remove(table)
        os.remove(dst)
        
        return
    
    def fake_tif(self):
        """create a fake tif of defined shap with only 0s"""
        
        # create a dataset 
        shape = (1, 60, 60)
        data = np.zeros(shape, dtype=np.uint8)
        
        # burn it into a file 
        file = tmp_dir.joinpath('add_pct.tif')
        
        kwargs = {
            'driver': 'GTiff', 
            'dtype': 'uint8', 
            'width': shape[0], 
            'height': shape[1], 
            'count': 1, 
            'crs': rio.crs.CRS.from_epsg(4326), 
            'tiled': False, 
            'compress': 'lzw', 
            'interleave': 'band'
        }
        
        with rio.open(file, 'w', **kwargs) as dst:
            dst.write(data)
        
        return file
    
    def fake_table(self):
        """create a fake color table"""
        
        # create the file
        val  = [0, 1]
        r = [color_1[0], color_2[0]]
        g = [color_1[1], color_2[1]]
        b = [color_1[2], color_2[2]]
        alpha = [color_1[3], color_2[3]]
        
        df = pd.DataFrame({'value': val, 'r': r, 'g':g, 'b': b, 'alpha': alpha})
        
        #export the table
        table = tmp_dir.joinpath('color_palette.csv')
        df.to_csv(table, index=False, header=False)
        
        return table
        
        