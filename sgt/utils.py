
def custom_print(verbose=False):
    """return a print function that does nothing if the verbose parameter is set to false and everything if true"""
    
    if verbose:
        # print the message
        def v_print(msg):
            print(msg)
    else:
        # do nothing function
        v_print = lambda msg: None 
        
    return v_print