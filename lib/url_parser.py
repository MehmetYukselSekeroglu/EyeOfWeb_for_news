from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import urlsplit
from typing       import Dict
import requests
from .user_agent_tools import randomUserAgent
from .hash import sha1_imageHash
from .numpy_tools import load_ImageFromContext

__MODULE_LOG_NAME__ = "URL_PARSER"

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webm",
    ".jfif"
)

def is_safe_url__html(target_url,timeout_sec=10,req_headers:dict=None) -> tuple:
        try:
            request_header = {
                "User-Agent":randomUserAgent()
            }            
            if req_headers is not None:
                request_header = req_headers
                
                
            send_request = requests.head(url=target_url,timeout=timeout_sec,headers=request_header)
            if not send_request.ok:
                return False
                        
            content_type = send_request.headers.get("Content-Type")
            if "text/html" not in content_type.lower():
                return False
            
            if "text/html" in content_type.lower():
                return True
            
            return False
            
        
        except Exception as err:
            return False


def is_safe_image__any(target_url,timeout_sec=5,req_headers:dict=None) -> tuple:
        try:
            request_header = {
                "User-Agent":randomUserAgent()
            }            
            if req_headers is not None:
                request_header = req_headers
                
                
            send_request = requests.head(url=target_url,timeout=timeout_sec,headers=request_header)
            if not send_request.ok:
                return False
                        
            content_type = send_request.headers.get("Content-Type")

            extensions_veritf = False
            for ext in IMAGE_EXTENSIONS:
                if str(urlparse(target_url).path).endswith(ext):
                    extensions_veritf = True
                    break
            
            if "image/" in content_type or extensions_veritf :
                return True
            else:
                return False
            
        
        except Exception as err:
            return False
            
            
            

def prepare_url(target_url:str) -> dict:
    decoded_url = unquote(target_url)
    parsed_url  = urlparse(decoded_url)
    return {
        "origin":decoded_url,
        "protocol":parsed_url.scheme,
        "base_domain":parsed_url.netloc,
        "path":parsed_url.path,
        "etc":parsed_url.params + parsed_url.query 
    }




if __name__ == "__main__":
    print(prepare_url("https://apps.apple.com/tr/app/h%C3%BCrriyet-son-dakika-haberler/id307878588;par=en?l=tr&loc=1#fragment"))