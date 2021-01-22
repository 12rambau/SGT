# known bug of rasterio 
import os 
if 'GDAL_DATA' in os.environ: del os.environ['GDAL_DATA']
    
import argparse
import pathlib 

import rasterio as rio
from rasterio.windows import Window
from tqdm import tqdm
import numpy as np
import rasterstats as rstats
import pandas as pd
import geopandas as gpd

from sgt.utils import custom_print 

available_stats = [
    'min', # default
    'max', # default
    'mean', # default
    'count', # default
    'sum',
    'std',
    'median',
    'majority',
    'minority',
    'unique',
    'range',
    'nodata',
    'percentile',
    'all', # will use all the stats but hist
    'hist', # cannot be used with others 
]

def zonal_stat(src_rst, mask_vector, out_vector, measurments=available_stats[:4], verbose=False):
    """Compute statistics over value of the source raster for each geometry defined in the mask. results are displayed in a vector file. The user can choose the statistics he want to inclued in the final file
    
    Args : 
        src_rst (str) : path to the source raster
        mask_vector (str) : path to the vector mask 
        out_vector (str) : path to the output vector 
        measurment ([str], optional) : list of the measurment you want to perform. available measurments are :
            - min
            - max
            - mean
            - count
            - sum
            - std
            - median
            - majority
            - minority
            - unique
            - range
            - nodata
            - percentile
        the first 4 are the defaulted values. 'all' key word can also be used to perform all measurments. ['hist'] will perform an histogram of the categorical value of the raster. it will be the only stat performed if it is found in the list
        verbose (bool) : wether or not to display text
    """
    
    # apply the verbose option
    v_print = custom_print(verbose)
    
    # get the file parameters
    with rio.open(src_rst) as f:
        crs = f.crs
        nodata = f.nodata
    
    # open the mask and project it into the raster crs 
    gdf = gpd.read_file(mask_vector).to_crs(crs)
    
    categorical = False
    stats = None
    # filter the measurments
    
    if measurments: 
        if 'hist' in measurments:
            categorical = True
        elif 'all' in measurments:
            stats = available_stats[:len(available_stats) - 2 - 1]
        else:
            tmp = [stat for stat in measurments if stat in available_stats]
            stats = None if len(tmp)==0 else tmp
            
    # if categorical I need to fetch the potential values 
    if categorical:
        with rio.open(src_rst) as f:
            
            count = np.bincount(f.read(1).flatten())
            features = np.where(count!=0)[0]
            
            # remove the nodata value from the feature
            features = features[~np.isin(features, nodata)]
            
            print(features)
            del count
            
    
    # loop over the different geometry 
    # longer than using just rasterstats but then I cannot display any evolution informations
    tmp_res = {str(i):[] for i in features} if categorical else {i: [] for i in stats}

    with tqdm(total=len(gdf), disable= not verbose) as pbar:
        for index, row in gdf.iterrows():
            
            #update tqdm 
            pbar.update(1)
            
            # get the geometry coordinates 
            left, bottom, right, top = row.geometry.bounds
            
            with rio.open(src_rst) as f:
                
                # window inside the extends of the raster
                left = max(left, f.bounds.left)
                top = min(top, f.bounds.top)
                right = min(right, f.bounds.right)
                bottom = max(bottom, f.bounds.bottom)
                
                # creat the window over the geometry 
                tlx, tly = f.index(left, top)
                brx, bry = f.index(right, bottom)
                win = Window.from_slices((tlx, brx), (tly, bry))
                win_transform = f.window_transform(win)
                
                # read the data in the window
                data = f.read(1, window=win)
                
                # do a zonal stat on 1 geometry
                zs = rstats.zonal_stats(
                    [row.geometry], #there is only one geometry 
                    data, 
                    affine = win_transform, 
                    nodata = nodata, 
                    all_touched = True,
                    stats = stats,
                    categorical = categorical)[0]
                
                # free memory 
                del data
                
            # for categorical measurments I need to transform the index in int 
            if categorical:
                zs = {str(int(i)): zs[i] for i in zs}
                
            # fill the dictionary
            for idx in tmp_res:
                val = zs[idx] if idx in zs.keys() else 0
                tmp_res[idx].append(val)
        
    df = pd.DataFrame(tmp_res)
                    
    # create the result geodataframe
    stat_gdf = gpd.GeoDataFrame(
        df, 
        geometry = gdf.geometry,
        columns = [str(i) for i in tmp_res] + ['geometry'], # geopandas refuse int as column key
        crs = crs
    )
                
    # save it 
    stat_gdf.to_file(out_vector)
    
    return df, stat_gdf

if __name__ == "__main__":
    
    # write the description 
    descript = "Compute statistics over value of the source raster for each geometry defined in the mask. results are displayed in a vector file. The user can choose the statistics he want to inclued in the final file"
    
    # create a arg parser 
    parser = argparse.ArgumentParser(description=descript)
    parser.add_argument(
        '-i',
        dest = 'src_rst',
        metavar = 'source.tif',
        help = '(str) : path to the source raster',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-um',
        dest = 'mask',
        metavar = 'mask.shp',
        help = '(str) : path to the mask vector file',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-o',
        dest = 'out_vector',
        metavar = 'output.shp',
        help = '(str) : path to the output vector file',
        required = True,
        type = pathlib.Path
    )
    parser.add_argument(
        '-stat',
        dest = 'measurments',
        nargs="+",
        choices = available_stats,
        metavar = 'stat_a stat_b stat_c',
        help = '([str]) : list of the measurment you want to perform. Default to [min max count mean]. "all" key word can also be used to perform all measurments. [hist] cannot be used with others. Allowed values are '+', '.join(available_stats),
        required = False,
        type = pathlib.Path
    )
    parser.add_argument(
        '--no-v',
        dest = 'verbose',
        action='store_false',
        required = False,
        help = "remove the verbose option"
    ) 
    
    # read arguments
    args = parser.parse_args()
    
    # launch the function 
    zonal_stat(**vars(args))