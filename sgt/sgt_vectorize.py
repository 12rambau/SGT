import sys

def vectorize(src_rst, out_vector):
    """ transform the first band of a raster into a vector shapefile 
    
    Args : 
        src_rst (str) : path to the source raster
        out_vector (str) : path to the output vector file
        
    Return :
        out_vector
    """
    
    
    
    return out_vector

if __name__ == "__main__":
    
    # read arguments
    out_csv = sys.argv[sys.argv.index('-o') + 1]
    src_rst = sys.argv[sys.argv.index('-i') + 1]
    mask_vector = sys.argv[index('-s') + 1]
    
    # launch the function 
    res = his(src_rst, out_csv, mask_rst)
    
    # dispay result 
    if res:
        print(f'The zonal analysis have been created : {out_csv}')