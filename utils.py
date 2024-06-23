import pandas as pd
import numpy as np
import warnings; warnings.filterwarnings("ignore")
import re

def split_strip_extremes(text, left, right, sep='_'):
    
    text = text.split(left)[-1] if left != '' else text
    text = text.split(right)[0] if right != '' else text
    try:
        return list(map(float, text.split(sep)))
    except:
        return [np.nan, np.nan]


def numeric_review(output, rev_col='Reviews', expand=True):
    
    expanded = [rev_col+'_nums', rev_col+'_avg_perc']\
            if expand else rev_col+'_arr'
    output[expanded] = output[rev_col]\
                .apply(split_strip_extremes, args=('','%)',' (')).tolist()
    return output

