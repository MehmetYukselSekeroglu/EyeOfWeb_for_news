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
from .downloaders.imageFromUrl           import downloadImage_defaultSafe
from .user_agent_tools                   import randomUserAgent
import threading
import time
from concurrent.futures                          import ThreadPoolExecutor,as_completed
from HiveWebCrawler.Crawler                      import WebCrawler
from urllib.parse                                import unquote, urlunparse, urlparse
import concurrent.futures
from HiveWebCrawler.Crawler                 import WebCrawler
from insightface.app                        import FaceAnalysis
import cv2
    
    
    
    


def proccessImage(single_image_list:list, parsedCurrentTarget:dict,self_databaseToolkit:DatbaseToolkit,self_insightFaceApp:FaceAnalysis,currentTarget,newsTitle, newsDate ):
    _img_url = single_image_list
    _img_url = str(_img_url)
    if not _img_url.startswith("http://") and not _img_url.startswith("https://"):
        if _img_url.startswith(parsedCurrentTarget["base_domain"]):
            _img_url = parsedCurrentTarget["protocol"] +  "://" + _img_url
        else:
            
            if _img_url.startswith("#/"):
                _img_url = _img_url[2:]
                #print(f"!!!!!! {_img_url}")
            
            _img_url =parsedCurrentTarget["protocol"] + "://"+ parsedCurrentTarget["base_domain"] + "/" + _img_url
    
    _parsed_image_url = prepare_url(target_url=_img_url)
    _imageDataAndStatus = downloadImage_defaultSafe(target_url=_img_url)
    
    if not _imageDataAndStatus[0]:
        p_error(f"URL'den resim alınamadı: {_img_url} -> {_imageDataAndStatus[1]}")
        return
    
    try:
        _detectedFaces = self_insightFaceApp.get(_imageDataAndStatus[1])
    except Exception as err:
        #p_error(f"INSIGHTFACE ERR HANDLED: {err}")
        _detectedFaces = None
        pass
    
    if len(_detectedFaces) < 1:
        _detectedFaces = None
    
    
    p_info(f"Detected {str(len(_detectedFaces))} on {single_image_list}")
    if _detectedFaces == None:
        return
    
    _b = self_databaseToolkit.insert_all_ImageBased(face_list=_detectedFaces,
        baseDomain=parsedCurrentTarget["base_domain"],
        urlPath=parsedCurrentTarget["path"],
        urlPathEtc=parsedCurrentTarget["etc"],imageBaseDomain=_parsed_image_url["base_domain"]
        ,imageUrlPath=_parsed_image_url["path"],imageUrlPathEtc=_parsed_image_url["etc"],
        image_title=newsTitle,imageHash=_imageDataAndStatus[2],newsDate=newsDate)
    
    p_info(_b,"")
    print("-"*30)
    
    






class SingleNewsCrawler():
    
    def __init__(self,
                DatabaseToolkit_object:DatbaseToolkit,
                ConnectionPool_object:ConnectionPoolTools,
                FirstTargetAddress:str,
                ThreadSize:int,
                CONFIG:list,
                ignore_db:bool=False,
                ignore_content:bool=False,
                NewsTitle:str=None,
                NewsDate:str=None,
                insightfaceApp=None,
                 ) -> None:
        
        self.Crawler        = WebCrawler()
        self.dbToolkit      = DatabaseToolkit_object
        self.ConnToolkit    = ConnectionPool_object
        self.InsightfaceApp = insightfaceApp
        self.FirstTarget    = FirstTargetAddress
        self.TargetList     = []
        self.TargetList.append(self.FirstTarget)
        self.ignore_database= ignore_db
        self.ThreadSize = ThreadSize
        self.ignore_content = ignore_content
        self.NewsTitle = NewsTitle
        self.NewsDate = NewsDate
        
        
        
        
        
    def uniqList(self, target_list) -> list:
        
        new_list = []
        
        for element in target_list:
            if self.dbToolkit.check_crawled(element):
                continue
            else:
                new_list.append(element)
                
        element = list(set(target_list))
        return element
    
    def startCrawl(self) -> None:
        currentTarget   = None
        
        if currentTarget == None and len(self.TargetList) < 1:
            return
        if len(self.TargetList) > 0:
            currentTarget = self.TargetList.pop(0) 
        
        
        if not self.ignore_database:
            self.TargetList = self.uniqList(self.TargetList)
        
        
        self.TargetList = list(set(self.TargetList))
                
        
        isAddressCrawled = self.dbToolkit.check_crawled(raw_url=currentTarget)
        if isAddressCrawled and self.ignore_database == False:
            return
        
        
                
        print(f"thread içi: {self.ignore_content}")
        imageTargetList = []
        if not is_safe_url__html(currentTarget) and self.ignore_content == False:
            return
                
                
                
    
        crawlData = self.Crawler.send_request(
            target_url=currentTarget,
            timeout_sec=10,
            req_headers={
                "User-Agent":randomUserAgent()
            })
                
        if not crawlData["success"]:
            p_error(f"{currentTarget} -> {crawlData['message']}")
            return
        
        
        
        parsedCurrentTarget = prepare_url(currentTarget)
        
        emails_from_url = self.Crawler.crawl_email_address_from_response_href(crawlData["data"])
        phone_from_url = self.Crawler.crawl_phone_number_from_response_href(crawlData["data"])
        links_from_url = self.Crawler.crawl_links_from_pesponse_href(parsedCurrentTarget["base_domain"],crawlData["data"])
        image_from_url = self.Crawler.crawl_image_from_response(crawlData["data"],parsedCurrentTarget["base_domain"])
                
    
        _phone_list = []
        _email_list = []
    
                
                
                
        if len(emails_from_url["data_array"]) < 1:
            p_warn(f"No email detected on -> {currentTarget}")
            _email_list = None
        else:
            for single_email_list in emails_from_url["data_array"]:
                _email = single_email_list[1]
                _email_list.append(_email)
                
                
        if len(phone_from_url["data_array"]) < 1:
            p_warn(f"No phone detected on -> {currentTarget}")
            _phone_list = None
        else:
            for single_phone_list in phone_from_url["data_array"]:
                _phone = single_phone_list[1]
                _phone_list.append(_phone)
                
        _a = self.dbToolkit.insert_all_PageBased(
            baseDomain=parsedCurrentTarget["base_domain"],
            urlPath=parsedCurrentTarget["path"],
            urlPathEtc=parsedCurrentTarget["etc"],
            phoneNumber_list=_phone_list,
            emailAddress_list=_email_list
            )
        p_info(_a)
        
        
        for single_list in image_from_url["data_array"]:
            imageTargetList.append(single_list[0])
        
        
        imageTargetList = list(set(imageTargetList))
        p_info(f"{currentTarget} içerisindeki toplam resim adeti: {len(imageTargetList)}")
        
        lastCounter = 0
        
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.ThreadSize) as threadExec:
            for single_image_list in imageTargetList:
                lastCounter += 1
                threadExec.submit(proccessImage,single_image_list, parsedCurrentTarget,self.dbToolkit,self.InsightfaceApp,currentTarget,self.NewsTitle,self.NewsDate)
                #proccessImage(single_image_list, parsedCurrentTarget,self.dbToolkit,self.InsightfaceApp,currentTarget,self.NewsTitle,self.NewsDate)
        p_info(f"{currentTarget} taraması tamamlandı.")
        self.dbToolkit.set_crawled(currentTarget,is_crawled=True)
            
                    
    
                    
    
    
    
    
    