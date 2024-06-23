import sys, logging
from typing import List, Set, Dict, Tuple, Optional, Callable 

def get_logger(name='metallum.log', mode='w', display=True):
    logging.basicConfig(level=logging.INFO, encoding='utf-8')
    logger = logging.getLogger(__name__)
    logger.propagate = False
    
    filehandler = logging.FileHandler(filename=name, mode=mode, encoding='utf-8')
    logger.addHandler(filehandler)
    
    if display:
        strmhandler = logging.StreamHandler()
        logger.addHandler(strmhandler)
        
    return logger