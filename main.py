from .utils import *
from .crawlers import *
import os

def safe_write(filename, folder_path=None):
    if folder_path is None:
        return filename
    else:
        return os.path.join(os.makedirs(folder_path, exist_ok=True),filename)
    
def run(url, write_path=None, pull_discogs=False):
    
    band_pool = BandCrawler(base_url=url, wait_time=2)
    band_pool._crawl_pool_meta()
    pool = band_pool.meta.copy()
    pool.to_csv(safe_write("Bands.csv",write_path), index=False)

    if pull_discogs:
        pbc = PoolDiscogCrawler(pool, page_wait=1)
        out = pbc.thread_crawl(return_merged=True)
        out = numeric_review(out, rev_col='Reviews', expand=True)
        out.to_csv(safe_write('Discography.csv',write_path), index=False, encoding='utf-16')



# if __name__ == "__main__":

#     BASE_URL = "https://www.metal-archives.com/search/advanced/searching/bands?bandName=&genre=*funeral*&country=&yearCreationFrom=&yearCreationTo=&bandNotes=&status=&themes=&location=&bandLabelName=#bands"
#     TO_PATH = None

#     run(url=BASE_URL, write_path=TO_PATH, pull_discogs=True)