import sys

import rasterio as rio
import numpy as np

def stat(src_rst, out_csv, mask_rst):
    """ computes image histogram by segments. 
    
    Args : 
        src_rst (str) : path to the source raster
        out_csv (str) : path to the output csv file
        mask_rst (str, optional) : path to the mask raster (a labeled raster 0 being the background)
        
    Return :
        out_csv
    """
    # identify features in the mask
    features = None
    if mask_rst:
        with rio.open(mask_rst) as f:
            mask_flat = f.read(1).flatten()
        
        # count all the possible classes 
        count = np.bincount(mask_flat)
        
        # create a list of features that only keep the not null one
        features = [i in range(np.amax(mask_flat) + 1)]
        features = features[np.nonzero(count)]
        
        # remove 0 (its the background)
        features = features[1:]
        
        # release memory 
        del mask_flat
        
    # open mask and image 
    with rio.open(mask_rst) as mask_f, rio.open(src_rst) as src_f:
        mask = mask_f.read()
        src = src_f.read()
        
    # count the number of bands 
    # reshape src to have at least 1 band 
    if src.ndim == 2:
        src = src[np.newaxis, :, :]
    nb_bands = src.shape[0] 
    
    
    # create the dataset content
    mask_id = []
    size = []
    bands = []
    avg = []
    std_dev = []
    min_ = []
    max_ = []
    
    # loop in each feature of the mask
    for feat in features:
        
        for band in range(nb_bands):
                
            # get the array of the masked value from src image
            # feat == 0 means that there is no mask
            if feat == 0:
                slice_ = src[i][mask != feat] 
            else:
                slice_ = src[i][mask == feat]
                
            # get the band content
            loc_size = slice_.shape[0]
            loc_avg = np.mean(slice_)
            loc_std = np.std(slice_)
            loc_min = np.amin(slice_)
            loc_max = np.amax(slice_)
            
            #wirte the line in the lists
            mask_id.append(feat)
            size.append(loc_size)
            bands.append(band)
            avg.append(loc_avg)
            std_dev.append(loc_std)
            min_.append(loc_min)
            max_.append(loc_max)
            
    
    # create the final dataframe 
    df = pd.DataFrame({
        'mask_id': mask_id,
        'frequency': size, 
        'band': bands, 
        'mean': avg, 
        'std_dev': std_dev, 
        'min': min_, 
        'max': max_
    })
    
    # export 
    df.to_csv(out_csv, index=False)
    
    return df

if __name__ == "__main__":
    
    # read arguments
    out_csv = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    mask_rst = sys.argv[index('-s') + 1]
    
    # launch the function 
    res = stat(src_rst, out_csv, mask_rst)
    
    # dispay result 
    if res:
        print(f'The segemented stats have been created : {out_csv}')