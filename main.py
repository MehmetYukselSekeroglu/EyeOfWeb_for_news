import feedparser
from lib.signle_page_crawler import SingleNewsCrawler
from lib.output.consolePrint import p_info,p_error,p_title,p_warn,p_log
from lib.user_agent_tools import randomUserAgent
from lib.output.banner                      import printBanner
from lib.load_config                        import load_config_from_file
from lib.database_toolkit                   import ConnectionPoolTools
from lib.database_toolkit                   import DatbaseToolkit
import sys
import os
import psycopg2
from lib.init_insightface import initilate_insightface
import time 
#Global varables 

global CONFIG
global PsqlConPool 
global InsightfaceMain 
global ThreadSize 
global ConnPoolSize 
global UrlFile



# ------------------ LOAD CONFIG AND CHECK AREA ----------------------
#? Main Config Varable  
CONFIG = load_config_from_file()

#? Checking config reading status 
if not CONFIG[0]:
    sys.exit(-1)



#? Thread size and pool size set
ThreadSize = CONFIG[1]["service"]["thread"]
ConnPoolSize = ThreadSize+ 5

# ------------------ END LOAD CONFIG AND CHECK AREA ----------------------


printBanner(CONFIG) # print current banner 



# ------------------ BEGIN DATABASE TOOLS AND CONNECTIONS --------------------

p_info("Initilating PostgreSQL Simple Connection pool.")
PsqlConPool = psycopg2.pool.SimpleConnectionPool(
        maxconn=ConnPoolSize,
        minconn=ConnPoolSize,
        **CONFIG[1]["database_config"]
        )

#? initilate database tools 
ConnPoolTools = ConnectionPoolTools(PsqlPool=PsqlConPool)
DatabaseTools = DatbaseToolkit(ConnPoolTools,CONFIG)


RSS_URL_FILE = "rss.txt"
RSS_URL_ARRAY = []


p_info(f"Loading rss from file: {str(RSS_URL_FILE)}")

with open(RSS_URL_FILE, "r",encoding="utf-8") as rssFile:
    for line in rssFile:
        line = line.strip()
        RSS_URL_ARRAY.append(line)
        

p_info(f"Loaded {str(len(RSS_URL_ARRAY))} rss url")

insightFaceApp = initilate_insightface(main_conf=CONFIG)

while True:
    for rssLink in RSS_URL_ARRAY:
        
        try:
            feed = feedparser.parse(rssLink)
            feed:feedparser.util.FeedParserDict
        except Exception as err:
            p_error(err)
            time.sleep(1)
            continue
        
        for singleDict in feed.entries:
            try:
                entryTitle = singleDict.title
                entryLink = singleDict.link
                entryPublished = singleDict.published
                WebEye = SingleNewsCrawler(DatabaseToolkit_object=DatabaseTools,ConnectionPool_object=ConnPoolTools,FirstTargetAddress=entryLink,ThreadSize=ThreadSize,CONFIG=CONFIG,ignore_db=False,ignore_content=True,NewsDate=entryPublished,NewsTitle=entryTitle,insightfaceApp=insightFaceApp)
                WebEye.startCrawl()
            except Exception as err:
                p_error(err)
                continue
    p_info(f"Sleeping 3600 sec")
    time.sleep(3600)





