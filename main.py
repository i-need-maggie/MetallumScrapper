from .utils import *
from .crawlers import *
import os

def safe_write(filename, folder_path=None):
    if folder_path is None:
        return filename
    else:
        return os.path.join(os.makedirs(os.path.dirname(folder_path), exist_ok=True),filename)
    
def main(base_url, write_path=None):
    
    band_pool = BandCrawler(base_url=BASE_URL, wait_time=2)
    band_pool._crawl_pool_meta()
    pool = band_pool.meta.copy()
    pool.to_csv(safe_write("Bands.csv",folder_path), index=False)

    pbc = PoolDiscogCrawler(pool, page_wait=1)
    out = pbc.thread_crawl(return_merged=True)
    out = numeric_review(out, rev_col='Reviews', expand=True)
    out.to_csv(safe_write('Discography.csv',folder_path), index=False, encoding='utf-16')



if __name__ == "__main__":

    BASE_URL = "https://www.metal-archives.com/search/advanced/searching/bands?bandName=&genre=*funeral*&country=&yearCreationFrom=&yearCreationTo=&bandNotes=&status=&themes=&location=&bandLabelName=#bands"
    TO_PATH = None

    main(base_url=BASE_URL, write_path=TO_PATH)