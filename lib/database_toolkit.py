import psycopg2
import psycopg2.pool
import numpy
import cv2
import pickle
import datetime



from typing                 import Tuple
from typing                 import Dict
from concurrent.futures     import ThreadPoolExecutor,as_completed
from .output.consolePrint   import p_info,p_error,p_warn
from .                      import sql_commands as sql
from .numpy_tools           import buffer2numpy_float32
from .numpy_tools           import compute_cosine_sim
from .                      import url_parser
from .opencv_tools          import export_kps_as_json

__MODULE_LOG_NAME__ = "DATABASE_TOOL"


#? Pool controller class 
class ConnectionPoolTools():
    def __init__(self, PsqlPool:psycopg2.pool.SimpleConnectionPool,) -> None:
        self.PsqlConnPool = PsqlPool
    
    
    def getConnection(self) -> psycopg2.extensions.connection:
        #? Get Connection From Pool 
        return self.PsqlConnPool.getconn()
    #? Local libs 

    def releaseConnection(self,conn:psycopg2.extensions.connection) -> None:
        #? Put Connection on Pool 
        self.PsqlConnPool.putconn(conn=conn)

    def closeAllConn(self) -> None:
        #? Close All Connection for exit protocol 
        self.PsqlConnPool.closeall()


        
class FaceSearchEngine():
    def __init__(self, connPoolTools:ConnectionPoolTools, config:list) -> None:
        #? Get global varables and set class varables 
        self.connPoolTool = connPoolTools
        self.config = config       

    def searchFaceOnDatabase(self, targetFaceData:dict, minSimilartiy:float=None,limit=None,search_thread:int=None) -> None:
        db = self.connPoolTool.getConnection()
        db_cursor = db.cursor()
        
        if minSimilartiy == None:
            minSimilartiy = self.config[1]["insightface_min_verification_sim"]
        
        if search_thread == None:
            search_thread = self.config[1]["service"]["thread"]
        
        db_cursor.execute(sql.GET_ALL_FACE_ON_DB)
        
        successAddDict = {}
        
        targetFace_embedding = targetFaceData["embedding"]
        
        def search_engine_thread(currentFaceTuple,targetFaceEmbedding:numpy.ndarray, minSim:float=minSimilartiy,successDict:dict=successAddDict ) -> None:
            try:    
                current_face_embeddings = buffer2numpy_float32(currentFaceTuple[1])
                similarity_rate = compute_cosine_sim(targetFaceEmbedding,current_face_embeddings)
                if similarity_rate > minSim:
                    successAddDict[str(currentFaceTuple[0])] = similarity_rate
            
            except Exception as err:
                p_error(err, locations=__MODULE_LOG_NAME__)
        
        
        with ThreadPoolExecutor(max_workers=search_thread) as thread_controller:
            while True:
                
                currentFaceTuple = db_cursor.fetchone()
                
                if not currentFaceTuple:
                    break
                
                
                thread_controller.submit(search_engine_thread,currentFaceTuple,targetFace_embedding)
                
                
        
        if len(successAddDict) == 0:
            return {
                "success":False,
                "message":"No match found in database",
                "data":None
            }
        
        else:
            return {
                "success":True,
                "message":"proccess success",
                "data":successAddDict
            }
                        
                        
        
class DatbaseToolkit():
    #! Main Database Tool Class 
    def __init__(self, connPoolTools:ConnectionPoolTools, config:list) -> None:
        #? Get global varables and set class varables 
        self.connPoolTool = connPoolTools
        self.config = config

    def set_preCrawlStatus(self,status:bool=False) -> bool:
        _static_key = "first_crawl"
        db_conn = self.connPoolTool.getConnection()
        db_cursor = db_conn.cursor()
        try:
            STATIC_SQL_COMMAND = """SELECT "key","val" FROM "DbInfo" WHERE "key"=%s """
            STATIC_DATA_TUPLE = (_static_key,)
            
            db_cursor.execute(STATIC_SQL_COMMAND, STATIC_DATA_TUPLE)
            results_is = db_cursor.fetchall()
            
            if len(results_is) < 1:
                STATIC_SQL_COMMAND = """INSERT INTO "DbInfo" ("key" ,"val") VALUES (%s, %s) """
                STATIC_DATA_TUPLE = (_static_key, bool(status))
                db_cursor.execute(STATIC_SQL_COMMAND, STATIC_DATA_TUPLE)
                db_conn.commit()
                
            else:
                STATIC_SQL_COMMAND = """UPDATE "DbInfo" SET "val"=%s WHERE "key"=%s """
                STATIC_DATA_TUPLE = (bool(status),_static_key)
                db_cursor.execute(STATIC_SQL_COMMAND, STATIC_DATA_TUPLE)
                db_conn.commit()
                
            self.connPoolTool.releaseConnection(db_conn)
            return True
                
        except Exception as err:
            self.connPoolTool.releaseConnection(db_conn)
            return False


    def get_preCrawlStatus(self) -> bool:
        _static_key = "first_crawl"
        db_conn = self.connPoolTool.getConnection()
        db_cursor = db_conn.cursor()
        try:
            STATIC_SQL_COMMAND = """SELECT "val" FROM "DbInfo" WHERE "key"=%s """
            STATIC_DATA_TUPLE = (_static_key,)
            
            db_cursor.execute(STATIC_SQL_COMMAND, STATIC_DATA_TUPLE)
            results_is = db_cursor.fetchall()
            
            if len(results_is) < 1:
                self.connPoolTool.releaseConnection(db_conn)
                return False
            
            else:
                self.connPoolTool.releaseConnection(db_conn)
                return results_is[0][0]
            
        
        except Exception as err:
            print(err)
            self.connPoolTool.releaseConnection(db_conn)
            return False
    


    def check_crawled(self, raw_url:str) -> bool:
        db_conn = self.connPoolTool.getConnection()
        db_cursor = db_conn.cursor()
        
        try:
            
            
            url_data = url_parser.prepare_url(raw_url)
            base_dom = str(url_data["base_domain"])
            url_path = str(url_data["path"])
            url_etc  = str(url_data["etc"])
            
            
            if url_path.startswith("/"):
                url_path = url_path[1:]
                
                        
            STATIC_DATA_TUPLE = (base_dom, url_path, url_etc)
            
            
            db_cursor.execute(sql.CHECK_IS_CRAWLED, STATIC_DATA_TUPLE)
            results_is = db_cursor.fetchall()


            if base_dom.startswith("www."):
                base_dom_2 = str(base_dom).replace("www.","")
            else:
                base_dom_2 = "www." + base_dom
            
            STATIC_DATA_TUPLE = (base_dom_2, url_path, url_etc)
            
            
            db_cursor.execute(sql.CHECK_IS_CRAWLED, STATIC_DATA_TUPLE)
            results_is2 = db_cursor.fetchall()

            db_cursor.close()
            self.connPoolTool.releaseConnection(db_conn)
            
            """
            print(f"results_is: {str(results_is)}")
            print(f"results_is2: {str(results_is2)}")
            """
            
            if len(results_is2) == 0 and len(results_is) == 0:
                return False
            else:
                return True
        
        except Exception as err:
            self.connPoolTool.releaseConnection(db_conn)
            p_error(err)
            return False
        
        
    def set_crawled(self,raw_url ,is_crawled:bool=True) -> None:
        db_conn = self.connPoolTool.getConnection()
        db_cursor = db_conn.cursor()
        
        try:
            
            url_data = url_parser.prepare_url(raw_url)
            base_dom = str(url_data["base_domain"])
            url_path = str(url_data["path"])
            url_etc  = str(url_data["etc"])
            if url_path.startswith("/"):
                url_path = url_path[1:]
                
            STATIC_DATA_TUPLE = (base_dom, url_path, url_etc)
            db_cursor.execute(sql.INSERT_IS_CRAWLED, STATIC_DATA_TUPLE)
            db_conn.commit()
            self.connPoolTool.releaseConnection(db_conn)
        except Exception as err:
            self.connPoolTool.releaseConnection(db_conn)
            p_error(err)
        
        
    def init_database_schema(self) -> Tuple[bool, str]:
        #? Exectue database schema (.sql) 
        #! Not required 
        #! use linux.sh --prepare-psql 
        
        # Set varables 
        db_schema = None
        db_conn = self.connPoolTool.getConnection()
        db_cursor = db_conn.cursor()
        
        # Try block for error handling 
        try:
            # open sql file and read 
            with open(self.config["database_schema"], "r") as schema_file:
                db_schema = schema_file.read()
            
            # execute and commit && feedback 
            db_cursor.execute(db_schema)
            db_conn.commit()
            self.connPoolTool.releaseConnection(db_conn)
            return (True, "Database schema succesfully initilated")
               
        # For Error Handling And Feddback  
        except Exception as err:
            self.connPoolTool.releaseConnection(db_conn)
            return (False, f"Failed to initilate database schema: {err}")
        
    
    
        
        
    def insert_all_PageBased(self,
            baseDomain,
            urlPath,
            urlPathEtc,
            phoneNumber_list:list=None,
            emailAddress_list:list=None,
            categortyNmae:str=None

            ) -> Tuple[int]:
        #! Get database conn 
        db = self.connPoolTool.getConnection()
        db_cursor = db.cursor()
        
        baseDomain_return_id = None
        urlPath_return_id = None
        urlPathEtc_return_id = None
        
        phoneNumber_return_id_LIST = []
        emailAddress_return_id_LIST = []
        categortyNmae_return_id = None

        
        
        try:
            
            if phoneNumber_list == None and emailAddress_list == None:
                self.connPoolTool.releaseConnection(db)
                return (True,"Not required data") 

            
            if phoneNumber_list != None:
                phoneNumber_list = list(set(phoneNumber_list))
            # ------------------- Phone Number's ---------------------------
                for phone_num in phoneNumber_list:
                    phone_num = str(phone_num)
                    phone_num = phone_num.strip()
                    phone_num = phone_num.replace(" ","")
                    phone_num = phone_num.replace("/","")
                    
                    
                    STATIC_DATA_TUPLE = (phone_num,)
                    
                    db_cursor.execute(sql.CHECK_PHONE_EXISTS, STATIC_DATA_TUPLE)
                    result_is = db_cursor.fetchall()
                    
                    if len(result_is) < 1:
                        db_cursor.execute(sql.INSERT_PHONE_RETURN_ID, STATIC_DATA_TUPLE)
                        result_is = db_cursor.fetchall()[0][0]
                        db.commit()
                        
                    else:
                        result_is = result_is[0][0]             
           
                    phoneNumber_return_id_LIST.append(result_is)

                phoneNumber_return_id_LIST = list(set(phoneNumber_return_id_LIST))
            # ----------------------------- Email Address ------------------------------
            
            if emailAddress_list != None:
                emailAddress_list = list(set(emailAddress_list))

            
                for email_addres in emailAddress_list:
                    email_addres = str(email_addres)
                    email_addres = email_addres.strip()
                    email_addres = email_addres.replace(" ","")
                    email_addres = email_addres.lower()
                    
                    STATIC_DATA_TUPLE = (email_addres,)
                    
                    db_cursor.execute(sql.CHECK_EMAIL_EXISTS, STATIC_DATA_TUPLE)
                    result_is = db_cursor.fetchall()
                    
                    if len(result_is) < 1:
                        db_cursor.execute(sql.INSERT_EMAIL_RETURN_ID, STATIC_DATA_TUPLE)
                        result_is = db_cursor.fetchall()[0][0]
                        db.commit()
                    else:
                        result_is = result_is[0][0]                        
                    
                    emailAddress_return_id_LIST.append(result_is)

                emailAddress_return_id_LIST = list(set(emailAddress_return_id_LIST))

            # ----------------------------- Category Name ------------------------------

            if categortyNmae != None:
                
                STATIC_DATA_TUPLE = (str(categortyNmae), )
                
                db_cursor.execute(sql.CHECK_CATEGORY_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_CATEGORY_RETURN_ID, STATIC_DATA_TUPLE)
                    categortyNmae_return_id = db_cursor.fetchall()[0][0]
                    db.commit()

                else:
                    categortyNmae_return_id = result_is[0][0]    





            
            # --------------------------- URL PATH ----------------------------------
            if urlPath != None:
                urlPath = str(urlPath)
                
                if urlPath.startswith("/"):
                    urlPath = urlPath[1:]
                
                STATIC_DATA_TUPLE = (str(urlPath), )
                db_cursor.execute(sql.CHECK_URLPATH_EXISTS, STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()

                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_URLPATH_RETURN_ID, STATIC_DATA_TUPLE)
                    urlPath_return_id = db_cursor.fetchall()[0][0]
                    db.commit()
                else:
                    urlPath_return_id = result_is[0][0]
            
            # --------------------------- Url Path Etc  ----------------------------------

            if urlPathEtc != None:
                STATIC_DATA_TUPLE = (str(urlPathEtc), )
                db_cursor.execute(sql.CHECK_URLETC_EXISTS, STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()

                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_URLETC_RETURN_ID, STATIC_DATA_TUPLE)
                    urlPathEtc_return_id = db_cursor.fetchall()[0][0]
                    db.commit()
                else:
                    urlPathEtc_return_id = result_is[0][0]


            # --------------------------- Base Domain  ----------------------------------


            if baseDomain != None:
                
                STATIC_DATA_TUPLE = (str(baseDomain), )
                
                db_cursor.execute(sql.CHECK_BASEDOMAIN_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_BASEDOMAIN_RETURN_ID, STATIC_DATA_TUPLE)
                    baseDomain_return_id = db_cursor.fetchall()[0][0]
                    db.commit()
                else:
                    baseDomain_return_id = result_is[0][0]

            # --------------------------- Page Based Maın Table Insert ----------------------------------

            STATIC_DATA_TUPLE = (
                baseDomain_return_id,
                urlPath_return_id,
                urlPathEtc_return_id,
                categortyNmae_return_id,
                phoneNumber_return_id_LIST,
                emailAddress_return_id_LIST,
                
            )
            
            db_cursor.execute(sql.CHECK_MAIN_PAGEBASED_EXISTS, STATIC_DATA_TUPLE)
            result_is = db_cursor.fetchall()
            
            if len(result_is) < 1:
                db_cursor.execute(sql.INSERT_MAIN_PAGEBASED, STATIC_DATA_TUPLE)
                db.commit()
            
            
            self.connPoolTool.releaseConnection(db)
            return (True,STATIC_DATA_TUPLE) 
        







        except Exception as err:
            #! Handle error put connections
            self.connPoolTool.releaseConnection(db)
            return (False, err)
            
        
    def insert_all_ImageBased(self, 
            face_list, 
            baseDomain,
            urlPath,
            urlPathEtc,
            imageBaseDomain,
            imageUrlPath,
            imageUrlPathEtc,
            image_title,
            imageHash,
            phoneNumber=None,
            emailAddress=None,
            imageData=None,
            categortyNmae=None,
            newsDate:str=None
            ) -> Tuple[int]:
        
        
        
        
        newsDate = datetime.datetime.fromisoformat(newsDate)
        
        #! Get database conn 
        db = self.connPoolTool.getConnection()
        db_cursor = db.cursor()
        
        
        # return id varables 
        FACE_ID_LIST = []
        baseDomain_return_id = None
        imageBaseDomain_return_id = None
        phoneNumber_return_id = None
        emailAddress_return_id = None
        imageHash_return_id = None
        categortyNmae_return_id = None
        imageStorage_return_id = None
        urlPath_return_id = None
        urlPathEtc_return_id = None
        imageTitle_return_id = None
        imageUrlPath_return_id = None
        imageUrlPathEtc_return_id = None
        
        try:         
            
            # --------------------------- Image Hash ----------------------------------
            if imageHash != None:
                
                STATIC_DATA_TUPLE = (str(imageHash), )
                
                db_cursor.execute(sql.CHECK_IMAGEHASH_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_IMAGEHASH_RETURN_ID, STATIC_DATA_TUPLE)
                    imageHash_return_id = db_cursor.fetchall()[0][0]

                else:
                    imageHash_return_id = result_is[0][0]
                    db_cursor.execute(sql.GET_HASH_BY_MAIN, (imageHash_return_id, ))
                    
                    result_is = db_cursor.fetchall()[0]
                    FACE_ID_LIST = result_is[9]
                    face_list = None              

            
      
            
            # --------------------------- FACE ID -------------------------------
            if face_list != None:
                for face_dict in face_list:
                    STATIC_DATA_TUPLE = (
                        psycopg2.Binary(face_dict["embedding"]),
                        psycopg2.Binary(face_dict["landmark_2d_106"]),
                        psycopg2.Binary(face_dict["bbox"]),
                        float(face_dict["det_score"]),
                        bool(face_dict["gender"]),
                        (face_dict["age"])
                    )

                    
                    #db_cursor.execute(sql.CHECK_FACE_EXISTS, STATIC_DATA_TUPLE)
                    #result_is = db_cursor.fetchall()
                    
                    #if len(result_is) < 1:
                    
                    db_cursor.execute(sql.INSERT_FACE_RETURN_ID, STATIC_DATA_TUPLE)
                    result_is = db_cursor.fetchall()[0][0]
                    db.commit()
                    
                    #else:
                    #    result_is = result_is[0][0]
                    
                    FACE_ID_LIST.append(result_is)

            """     #! Reference
                    STATIC_DATA_TUPLE = (phone_num,)
                    
                    db_cursor.execute(sql.CHECK_PHONE_EXISTS, STATIC_DATA_TUPLE)
                    result_is = db_cursor.fetchall()
                    
                    if len(result_is) < 1:
                        db_cursor.execute(sql.INSERT_PHONE_RETURN_ID, STATIC_DATA_TUPLE)
                        result_is = db_cursor.fetchall()[0][0]
                        db.commit()
                        
                    else:
                        result_is = result_is[0][0]             
           
                    phoneNumber_return_id_LIST.append(result_is)

                phoneNumber_return_id_LIST = list(set(phoneNumber_return_id_LIST))
            
            """
            
            # --------------------------- URL PATH ----------------------------------
            if urlPath != None:
                urlPath = str(urlPath)
                if urlPath.startswith("/"):
                    urlPath = urlPath[1:]                
                
                STATIC_DATA_TUPLE = (urlPath, )
                db_cursor.execute(sql.CHECK_URLPATH_EXISTS, STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()

                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_URLPATH_RETURN_ID, STATIC_DATA_TUPLE)
                    urlPath_return_id = db_cursor.fetchall()[0][0]
                else:
                    urlPath_return_id = result_is[0][0]
            
            # --------------------------- Url Path Etc  ----------------------------------

            if urlPathEtc != None:
                STATIC_DATA_TUPLE = (str(urlPathEtc), )
                db_cursor.execute(sql.CHECK_URLETC_EXISTS, STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()

                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_URLETC_RETURN_ID, STATIC_DATA_TUPLE)
                    urlPathEtc_return_id = db_cursor.fetchall()[0][0]
                else:
                    urlPathEtc_return_id = result_is[0][0]
            
            
            # --------------------------- image_title  ----------------------------------
            
            if image_title != None:
                
                STATIC_DATA_TUPLE = (str(image_title), )
                db_cursor.execute(sql.CHECK_TITLE_EXISTS, STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()

                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_TITLE_RETURN_ID, STATIC_DATA_TUPLE)
                    imageTitle_return_id = db_cursor.fetchall()[0][0] 
                else:
                    imageTitle_return_id = result_is[0][0]
                
            # --------------------------- Image Url Path  ----------------------------------

            if imageUrlPath != None:
                
                STATIC_DATA_TUPLE = (str(imageUrlPath), )
                db_cursor.execute(sql.CHECK_IMAGE_URLPATH_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()

                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_IMAGE_URLPATH_RETURN_ID, STATIC_DATA_TUPLE)
                    imageUrlPath_return_id = db_cursor.fetchall()[0][0]

                else:
                    imageUrlPath_return_id = result_is[0][0]
            

            # --------------------------- Image Url Path Etc  ----------------------------------

            if imageUrlPathEtc != None:
                
                STATIC_DATA_TUPLE = (str(imageUrlPathEtc), )
                
                db_cursor.execute(sql.CHECK_IMAGE_URLETC_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                
                    db_cursor.execute(sql.INSERT_IMAGE_URLETC_RETURN_ID, STATIC_DATA_TUPLE)
                    imageUrlPathEtc_return_id = db_cursor.fetchall()[0][0]

                else:
                    imageUrlPathEtc_return_id = result_is[0][0]
            
            
            # --------------------------- Base Domain  ----------------------------------

            if baseDomain != None:
                baseDomain = str(baseDomain)
                baseDomain = baseDomain.replace("www.","")
                
                STATIC_DATA_TUPLE = (str(baseDomain), )
                
                db_cursor.execute(sql.CHECK_BASEDOMAIN_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_BASEDOMAIN_RETURN_ID, STATIC_DATA_TUPLE)
                    baseDomain_return_id = db_cursor.fetchall()[0][0]

                else:
                    baseDomain_return_id = result_is[0][0]

            # --------------------------- Image Base Domain  ----------------------------------

            if imageBaseDomain != None:
                imageBaseDomain = str(imageBaseDomain)
                imageBaseDomain = imageBaseDomain.replace("www.","")
                STATIC_DATA_TUPLE = (str(imageBaseDomain), )
                
                db_cursor.execute(sql.CHECK_BASEDOMAIN_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_BASEDOMAIN_RETURN_ID, STATIC_DATA_TUPLE)
                    imageBaseDomain_return_id = db_cursor.fetchall()[0][0]

                else:
                    imageBaseDomain_return_id = result_is[0][0]


            # --------------------------- Phone Number  ----------------------------------
            if phoneNumber != None:
                #! for dongüsü eklenecek bu bir liste olarak alınacak!
                STATIC_DATA_TUPLE = (str(phoneNumber), )
                
                db_cursor.execute(sql.CHECK_PHONE_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_PHONE_RETURN_ID, STATIC_DATA_TUPLE)
                    phoneNumber_return_id = db_cursor.fetchall()[0][0]

                else:
                    phoneNumber_return_id = result_is[0][0]

            # --------------------------- Email Address  ----------------------------------
            if emailAddress != None:
                #! for dongüsü eklenecek bu bir liste olarak alınacak!
                STATIC_DATA_TUPLE = (str(emailAddress), )
                
                db_cursor.execute(sql.CHECK_EMAIL_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_EMAIL_RETURN_ID, STATIC_DATA_TUPLE)
                    emailAddress_return_id = db_cursor.fetchall()[0][0]

                else:
                    emailAddress_return_id = result_is[0][0]

            # --------------------------- Category Name ----------------------------------
            if categortyNmae != None:
                
                STATIC_DATA_TUPLE = (str(categortyNmae), )
                
                db_cursor.execute(sql.CHECK_CATEGORY_EXISTS,STATIC_DATA_TUPLE)
                result_is = db_cursor.fetchall()
                
                if len(result_is) < 1:
                    db_cursor.execute(sql.INSERT_CATEGORY_RETURN_ID, STATIC_DATA_TUPLE)
                    categortyNmae_return_id = db_cursor.fetchall()[0][0]

                else:
                    categortyNmae_return_id = result_is[0][0]    

            # --------------------------- Image Storage ----------------------------------

            if self.config[1]["service"]["save_images"]:
                if imageData != None:
                    STATIC_DATA_TUPLE = (psycopg2.Binary(imageData), )

                    db_cursor.execute(sql.CHECK_CATEGORY_EXISTS,STATIC_DATA_TUPLE)
                    result_is = db_cursor.fetchall()

                    if len(result_is) < 1:
                        db_cursor.execute(sql.INSERT_CATEGORY_RETURN_ID, STATIC_DATA_TUPLE)
                        categortyNmae_return_id = db_cursor.fetchall()[0][0]

                    else:
                        categortyNmae_return_id = result_is[0][0]    

            
                
            # --------------------------- Image Based Maın Table Insert ----------------------------------

            STATIC_DATA_TUPLE = (
                baseDomain_return_id,
                urlPath_return_id,
                urlPathEtc_return_id,
                imageBaseDomain_return_id,
                imageUrlPath_return_id,
                imageUrlPathEtc_return_id,
                imageTitle_return_id,
                imageStorage_return_id,
                FACE_ID_LIST,
                categortyNmae_return_id,
                imageHash_return_id,
                phoneNumber_return_id,
                emailAddress_return_id,
                newsDate
            )
            
            CHECK_TUPLE  = (
                baseDomain_return_id,
                urlPath_return_id,
                urlPathEtc_return_id,
                imageBaseDomain_return_id,
                imageUrlPath_return_id,
                imageUrlPathEtc_return_id,
                imageHash_return_id
            )
            db_cursor.execute(sql.CHECK_MAIN_IMAGEBASED_EXISTS, CHECK_TUPLE)
            result_is = db_cursor.fetchall()
            if len(result_is) < 1:
                db_cursor.execute(sql.INSERT_MAIN_IMAGEBASED, STATIC_DATA_TUPLE)
                db.commit()
                self.connPoolTool.releaseConnection(db)
                return (True,STATIC_DATA_TUPLE) 
            else:
                self.connPoolTool.releaseConnection(db)
                return (True,f"This Combination Alredy Exists: {STATIC_DATA_TUPLE[1]}")    

        
        except UnicodeDecodeError as err:
            #! Handle error put connections
            self.connPoolTool.releaseConnection(db)
            return (False, err)
            
   
        

