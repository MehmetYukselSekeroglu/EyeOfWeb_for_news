#!/usr/bin/env python3


# ? Local Librarys 
from .output.consolePrint                import p_info, p_error, p_warn,p_log
from .load_config                        import load_config_from_file
from .init_insightface                   import initilate_insightface
from .output.banner                      import printBanner
from .database_toolkit                   import ConnectionPoolTools
from .database_toolkit                   import DatbaseToolkit
from .url_parser                         import prepare_url, IMAGE_EXTENSIONS
from .url_parser                         import is_safe_image__any,is_safe_url__html
from .downloaders.imageFromUrl           import get_ImageFromUrl
from .user_agent_tools                   import randomUserAgent
from .threads.single_domain_thread       import single_domain_thread


# externel librarys

from concurrent.futures                          import ThreadPoolExecutor,as_completed
from HiveWebCrawler.Crawler                      import WebCrawler
from urllib.parse                                import unquote, urlunparse, urlparse

import numpy
import typing
import os
import argparse
import psycopg2.pool
import psycopg2
import insightface
import time
import sys
import threading
import cv2



class SingleDomainCrawler():
    
    def __init__(self,DatabaseToolkit_object:DatbaseToolkit,ConnectionPool_object:ConnectionPoolTools,FirstTargetAddress:str,ThreadSize:int,CONFIG:list,ignore_db:bool=False, ignore_content:bool=False,ORB=None) -> None:
        
        self.ORB            = ORB        
        self.Crawler        = WebCrawler()
        self.dbToolkit      = DatabaseToolkit_object
        self.ConnToolkit    = ConnectionPool_object
        self.InsightfaceApp = initilate_insightface(main_conf=CONFIG)
        self.FirstTarget    = FirstTargetAddress
        self.TargetList     = []
        self.TargetList.append(self.FirstTarget)
        self.ignore_database= ignore_db
        self.ThreadSize = ThreadSize
        self.ignore_content = ignore_content
        self.CrawledBuffer = []
        
        
    def uniqList(self, target_list) -> list:
        
        new_list = []
        
        for element in target_list:
            if self.dbToolkit.check_crawled(element):
                continue
            else:
                new_list.append(element)
                
        new_list = list(set(new_list))
        return new_list
    
    def startCrawl(self) -> None:
        
        
        
        while True:
            currentTarget   = None
            
            
            if currentTarget == None and len(self.TargetList) < 1:
                p_info("Herhangi bir hedef kalmadı döngüden çıkılıyor .")

                p_info("Thread'lar bekleniyor ...")
                
                while threading.activeCount() != 1:
                    time.sleep(0.1)
                
                p_info("Threadlar tamamlandı .")
                break

            if len(self.TargetList) > 0:
                currentTarget = self.TargetList.pop(0) 
            
            
            if not self.ignore_database:
                self.TargetList = self.uniqList(self.TargetList)
            else:
                self.TargetList = list(set(self.TargetList))
            
            
            self.TargetList = list(set(self.TargetList))
            
            print(f"[HEDEF]: {currentTarget}")
            print(f"[TOPLAM]: {len(self.TargetList)}")
            
            
            isAddressCrawled = self.dbToolkit.check_crawled(raw_url=currentTarget)

            if isAddressCrawled and self.ignore_database == False or currentTarget in self.CrawledBuffer:
                p_warn(f"{currentTarget} adresi taranmış, atlanıyor.")
                continue
            
            self.CrawledBuffer.append(currentTarget)
            
            if len(self.TargetList) > self.ThreadSize:
                while threading.activeCount() >= self.ThreadSize:
                    time.sleep(0.1)
                
                p_info("Yeni thread başlatılıyor...")
                threading.Thread(target=single_domain_thread, args=(currentTarget, self.Crawler, self.TargetList, self.dbToolkit, self.InsightfaceApp,self.ignore_content,self.ORB),daemon=True).start()
                continue
            else:
                single_domain_thread(currentTarget, self.Crawler, self.TargetList, self.dbToolkit, self.InsightfaceApp,ignore_content=self.ignore_content,self_OpencvOrb=self.ORB)
                continue
        

                




