from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

import pandas as pd
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from typing import List, Set, Dict, Tuple, Optional, Callable

from collections import *
from functools import *
from itertools import *

from dataclasses import dataclass
import re, math, time, logging

from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

from .driver import init_driver
from .logger import get_logger

logger = get_logger()


class BandCrawler(object):
    
    def __init__(
        self, 
        base_url:str,
        wait_time:int=4,
        page_crawls:Optional[int]=None
    ):
        self.base_url = base_url
        self.wait_time = wait_time
        self.page_crawls = page_crawls

        logger.info(f"{self.__class__.__name__} instantiated, with page wait: {self.wait_time} sec")

        self.driver = init_driver()
        self.driver.get(self.base_url)
        time.sleep(self.wait_time)
        
        entry_text = self.driver.find_element(By.XPATH, './/div[@class="dataTables_info"]').text
        self._easy_max_entry_info(entry_text)
        self._true_page_crawls = min(self.page_crawls,self.num_pages) if self.page_crawls else self.num_pages

    def _crawl_page_meta(self):
        
        foo = self.driver.find_element(By.ID, "searchResultsBand")
        
        head = foo.find_element(By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
        head = [val.text for val in head]
        
        body = foo.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
        cont = list(list(inner.text for inner in val.find_elements(By.TAG_NAME, "td")) for val in body)
            
        href = list(val.find_element(By.TAG_NAME, "a").get_attribute("href") for val in body)
        
        base = pd.DataFrame(cont, columns=head)
        base['href'] = href
        
        return base

    def _crawl_pool_meta(self):
        
        self.meta = self._crawl_page_meta()
        counter = 1
        
        while counter < self._true_page_crawls:
            counter += 1
            WebDriverWait(self.driver, 20)\
                    .until(EC.element_to_be_clickable((By.XPATH, './/a[@class="next paginate_button"][@tabindex="0"]'))).click()
            time.sleep(self.wait_time)
            logger.info(f"Info pulled from page: {counter}")
            
            try:
                pool = self._crawl_page_meta()
                self.meta = pd.concat((self.meta,pool), axis=0, ignore_index=True)
                
            except (StaleElementReferenceException, TimeoutException):
                raise TimeoutException("Page taking too long to load..")
            
        logger.info(f"Band info pulled from all {counter} pages, closing the driver..")
        self.driver.close()
        
    def _easy_max_entry_info(self, text):
        
        entry_info = list(map(int,re.sub(r'[A-Za-z]','',text).strip().replace('  ',' ').split(' ')))
        self.num_bands = entry_info[-1]
        self.bands_per_page = entry_info[1]-entry_info[0]+1
        self.num_pages = math.ceil(self.num_bands/self.bands_per_page)


class DiscogCrawler(object):
    def __init__(
        self, 
        base_url:str,
        wait_time:int=4,
        fetch_comments:bool=False
    ):
        self.base_url = base_url
        self.wait_time = wait_time
        self.fetch_comments = fetch_comments
        if self.fetch_comments:
            self._sub_driver = init_driver()

        logger.info(f"{self.__class__.__name__} instantiated, with page wait: {self.wait_time} sec")

        self.driver = init_driver()
        self.driver.get(self.base_url)
        time.sleep(self.wait_time)

    def crawl(self):

        # get band name
        name = self.driver.find_element(By.CLASS_NAME, "band_name").text
        # fetch discog section
        foo = self.driver.find_element(By.XPATH, './/div[@id="band_tab_discography"]')
        # pull header info
        head = foo.find_element(By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
        head = [val.text for val in head]
        # pull discog content info
        body = foo.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
        cont = list(list(inner.text.strip() for inner in val.find_elements(By.TAG_NAME, "td")) for val in body)
        hrefs, reviews = list(),list()
        for val in body:
            try:
                href = val.find_elements(By.TAG_NAME, 'td')[-1].find_element(By.TAG_NAME, 'a').get_attribute("href")
                hrefs.append(href)

                if self.fetch_comments:
                    self._sub_driver.get(href)
                    time.sleep(0.5)
                    sections = self.driver.find_elements(By.CLASS_NAME, "reviewBox")
                    headlines = list(map(lambda x:x.find_element(By.CLASS_NAME, "reviewTitle").text, sections))
                    comments = list(map(lambda x:x.find_element(By.CLASS_NAME, "reviewContent").text, sections))
                    review = '||'.join(list(map(lambda x:x[0]+'::'+x[-1], list(zip(headlines,comments)))))
                    reviews.append(review)
                else:
                    reviews.append('')
            except NoSuchElementException:
                hrefs.append('')
                reviews.append('')
                
        # create dataframe of discog content info
        try:
            base = pd.DataFrame(cont, columns=head)
            entries = len(body)
        except:
            base = pd.DataFrame(np.tile(np.array(''),(len(body),len(head))), columns=head)
            entries = 0
        base['href'] = hrefs
        base['Comments'] = reviews
        base['Band'] = name
        logger.info(f"finished pulling info for: {name}, #Discog: {entries}")
        self.driver.close()
        
        return base


class PoolDiscogCrawler(object):

    def __init__(
        self, 
        frame:pd.DataFrame, 
        href_col:str='href', 
        id_col:str='Name',
        page_wait:int=1,
        num_workers:Optional[int]=None
    ):
        self.frame = frame
        self.href_col = href_col
        self.id_col = id_col
        self.page_wait = page_wait
        self.num_workers = num_workers
        logger.info(
            f"{self.__class__.__name__} instantiated, # bands to be searched: {len(self.frame)}"
        )

    def thread_crawl(self, return_merged=True):
        
        hrefs = self.frame[self.href_col].tolist()
        submits = list()
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for href in hrefs:
                bndcrwl = DiscogCrawler(href,self.page_wait,False)
                submits.append(executor.submit(bndcrwl.crawl))
        # outputs = pd.concat([submit.result() for submit in submits], axis=0, ignore_index=True)
        self.outputs, self.failed = pd.DataFrame(), pd.DataFrame()
        self.failures = 0
        for submit in as_completed(submits):
            try:
                self.outputs = pd.concat((self.outputs,submit.result()), axis=0, ignore_index=True)
            except:
                self.failures += 1
                pass

        logger.info(f"# failed pulls: {self.failures}")
                
        if return_merged:
            outputs = self.frame.drop(self.href_col,axis=1)\
                    .merge(self.outputs,how='left',left_on=self.id_col,right_on='Band')
        
            return outputs

