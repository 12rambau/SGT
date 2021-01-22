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

nb_cell = 6 # number of grid cells in the starting element
crs = rio.crs.CRS.from_epsg(4326)
res = 0.00026949458523585647 # ~30m in deg
tmp_dir = Path('~', 'tmp').expanduser()
tmp_dir.mkdir(exist_ok=True)

###############################

class TestZonalStat(unittest.TestCase):
    
    def test_method(self):
        
        # create the fake material 
        src = self.fake_tif()
        shp = self.fake_shape()
        
        # create an hist dataframe 
        dst = tmp_dir.joinpath('result.shp')
        zonal_stat(src, shp, dst, ['hist'])
        
        # check the gdf 
        final_gdf = gpd.read_file(dst)
        expected_gdf = self.expected_result(shp)
        
        self.assertTrue(identical(final_gdf, expected_gdf))
        
        # destroy everything 
        self.del_shp(shp)
        self.del_shp(dst)
        src.unlink()
        
        return 
     
    def fake_tif(self):
        """fake a tif file"""
        
        # initialte parameters 
        bands, rows, cols = shape = (1, nb_cell, nb_cell)
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
            'transform': transform,
            'nodata': 0
        }
        
        with rio.open(file, 'w', **kwargs) as dst:
            dst.write(data)
        
        return file
    
    def fake_shape(self):
        """create a shahpaefile composed of 4 squares, that cross the tif file"""
        
        # initialise the gdf
        height = length = nb_cell * res
        west, south, east, north = -length/2, -height/2, length/2, height/2
    
        # create the gdf
        data = {
            'fixed_id' : [i+1 for i in range(4)],
            'geometry' : [
                sg.Point(west + length/4, south + 3*height/4),
                sg.Point(west + 3*length/4, south + 3*height/4),
                sg.Point(west + length/4, south + height/4),
                sg.Point(west + 3*length/4, south + height/4)
            ]
        }
        gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
        gdf.geometry = gdf.geometry.buffer(length/4, cap_style=3)
    
        # save the file
        file = tmp_dir.joinpath('shapes.shp')
        gdf.to_file(file)

        return file
    
    def expected_result(self, shp):
        """construct the expected gdf"""
        
        # fake data 
        data = {'10': [1, 1, 1, 2], '22': [6, 0, 0, 0], '36': [0, 1, 0, 0]}
        
        gdf = gpd.GeoDataframe(data, geometry=gpd.read_file(shp).geometry, crs=crs)
        
        return gdf
    
    def del_shp(self, file):
        "remove a shapefile and all the related file in the process"
        
        pattern = f'{file.stem}.*'
        file_list = tmp_dir.glob(pattern)
        
        for file in file_list:
            file.unlink()
        
        return
        