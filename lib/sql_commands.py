INSERT_FACE_RETURN_ID = """INSERT INTO "FaceStorageID" 
    ( "FaceEmbeddingData", "Landmarks2d", "FaceBox", "DetectionScore" , "FaceGender", "FaceAge" ) VALUES (%s, %s, %s, %s, %s, %s) RETURNING "ID" """
    
CHECK_FACE_EXISTS = """SELECT "ID" FROM "FaceStorageID" 
    WHERE "FaceEmbeddingData"=%s AND "Landmarks2d"=%s AND "FaceBox"=%s AND "DetectionScore"=%s AND "FaceGender"=%s AND "FaceAge"=%s """


INSERT_URLPATH_RETURN_ID = """INSERT INTO "UrlPathID" ( "Path" ) VALUES ( %s ) RETURNING "ID" """
CHECK_URLPATH_EXISTS = """SELECT "ID" FROM "UrlPathID" WHERE "Path"=%s """

INSERT_URLETC_RETURN_ID = """INSERT INTO "UrlEtcID" ( "Etc" ) VALUES ( %s ) RETURNING "ID" """
CHECK_URLETC_EXISTS = """SELECT "ID" FROM "UrlEtcID" WHERE "Etc"=%s """


INSERT_TITLE_RETURN_ID = """INSERT INTO "ImageTitleID" ( "Title" ) VALUES ( %s ) RETURNING "ID"  """
CHECK_TITLE_EXISTS = """SELECT "ID" FROM "ImageTitleID" WHERE "Title"=%s """


INSERT_IMAGE_URLPATH_RETURN_ID = """INSERT INTO "ImageUrlPathID" ( "Path" ) VALUES ( %s ) RETURNING "ID" """
CHECK_IMAGE_URLPATH_EXISTS = """SELECT "ID" FROM "ImageUrlPathID" WHERE "Path"=%s """


INSERT_IMAGE_URLETC_RETURN_ID = """INSERT INTO "ImageUrlEtcID" ( "Etc" ) VALUES ( %s ) RETURNING "ID" """
CHECK_IMAGE_URLETC_EXISTS = """SELECT "ID" FROM "ImageUrlEtcID" WHERE "Etc"=%s """


INSERT_BASEDOMAIN_RETURN_ID = """INSERT INTO "BaseDomainID" ( "Domain" ) VALUES ( %s ) RETURNING "ID" """
CHECK_BASEDOMAIN_EXISTS = """SELECT "ID" FROM "BaseDomainID" WHERE "Domain"=%s """


INSERT_PHONE_RETURN_ID = """INSERT INTO "PhoneNumberID" ("PhoneNumber" ) VALUES ( %s ) RETURNING "ID"  """
CHECK_PHONE_EXISTS = """SELECT "ID" FROM "PhoneNumberID" WHERE "PhoneNumber"=%s """


INSERT_EMAIL_RETURN_ID = """INSERT INTO "EmailAddressID" ( "EmailAddress" ) VALUES ( %s ) RETURNING "ID" """
CHECK_EMAIL_EXISTS = """SELECT "ID" FROM "EmailAddressID" WHERE "EmailAddress"=%s """


INSERT_RAWTEXT_RETURN_ID = """INSERT INTO "RawTextFromImageID" ( "RawText" ) VALUES ( %s ) RETURNING "ID"  """
CHECK_RAWTEXT_EXISTS = """SELECT "ID" FROM "RawTextFromImageID" WHERE "RawText"=%s """


INSERT_CARPLATE_RETURN_ID = """INSERT INTO "CarPlateNumberID" ( "PlateNumber" ) VALUES ( %s ) RETURNING "ID" """
CHECK_CARPLATE_EXISTS = """SELECT "ID" FROM "CarPlateNumberID" WHERE "PlateNumber"=%s """


INSERT_IMAGEHASH_RETURN_ID = """INSERT INTO "ImageHashID" ( "ImageHash" ) VALUES ( %s ) RETURNING "ID" """
CHECK_IMAGEHASH_EXISTS = """SELECT "ID" FROM "ImageHashID" WHERE "ImageHash"=%s """


INSERT_IMAGEEXIF_RETURN_ID = """INSERT INTO "ImageMetaDataID" ( "RawExif" ) VALUES ( %s ) RETURNING "ID" """
CHECK_IMAGEEXIF_EXISTS = """SELECT "ID" FROM "ImageMetaDataID" WHERE "RawExif"=%s """


INSERT_CATEGORY_RETURN_ID = """INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ( %s ) RETURNING "ID" """
CHECK_CATEGORY_EXISTS = """SELECT "ID" FROM "WebSiteCategoryID" WHERE "Category"=%s """


INSERT_IS_CRAWLED = """INSERT INTO "CrawledAddress" ( "BaseDomain", "BaseUrlPath", "BaseUrlEtc" ) VALUES ( %s, %s, %s ) """
CHECK_IS_CRAWLED = """SELECT * FROM "CrawledAddress" WHERE "BaseDomain"=%s AND "BaseUrlPath"=%s AND "BaseUrlEtc"=%s """


INSERT_ORB_RETURN_ID = """INSERT INTO "ImageOrbDataID" ("KeyPoints", "Description") VALUES (%s,%s) RETURNING "ID" """
CHECK_ORB_EXISTS = """SELECT "ID" FROM "ImageOrbDataID" WHERE "KeyPoints"=%s AND "Description"=%s """
GET_ALL_ORB_DATA = """SELECT * FROM "ImageOrbDataID" """



GET_ALL_FACE_ON_DB = """SELECT "ID","FaceEmbeddingData" FROM "FaceStorageID" """

GET_HASH_BY_MAIN = """SELECT * FROM "ImageBasedMain" WHERE "HashID"=%s"""


INSERT_MAIN_IMAGEBASED = """INSERT INTO "ImageBasedMain" 
    ( "BaseDomainID", "BaseUrlPathID", "BaseUrlEtcID", "ImageDomainID", "ImagePathID", "ImageUrlEtcID",
        "ImageTitleID", "ImageID", "FaceID", "CategoryID", "HashID", "PhoneID", "EmailID", "Date" ) VALUES 
            ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
        
CHECK_MAIN_IMAGEBASED_EXISTS = """SELECT "ID" FROM "ImageBasedMain" WHERE 
    "BaseDomainID"=%s AND "BaseUrlPathID"=%s AND "BaseUrlEtcID"=%s AND "ImageDomainID"=%s AND "ImagePathID"=%s AND
    "ImageUrlEtcID"=%s AND "HashID"=%s LIMIT 1"""
    
    

"""
#! Referance for page based 

CREATE TABLE IF NOT EXISTS "PageBasedMain" (
    "ID"            SERIAL PRIMARY KEY,
    "BaseDomainID"  BIGINT NOT NULL, 
    "UrlPathID"     BIGINT NOT NULL, 
    "BaseUrlEtcID"  BIGINT NOT NULL,
    "CategoryID"    SMALLINT DEFAULT NULL,
    "PhoneID"       BIGINT[] DEFAULT NULL,
    "EmailID"       BIGINT[] DEFAULT NULL,
    "PageTitleID"   BIGINT DEFAULT NULL,
    "Date" TIMESTAMP DEFAULT NOW()

);
"""

INSERT_MAIN_PAGEBASED = """INSERT INTO "PageBasedMain" 
    ( "BaseDomainID", "UrlPathID", "BaseUrlEtcID", "CategoryID", "PhoneID", "EmailID","Date" ) VALUES 
    ( %s,%s,%s, %s,%s,%s,%s)"""
    
    
CHECK_MAIN_PAGEBASED_EXISTS = """SELECT "ID" FROM "PageBasedMain" WHERE 
    "BaseDomainID"=%s AND "UrlPathID"=%s AND "BaseUrlEtcID"=%s AND "CategoryID"=%s AND "PhoneID"=%s AND "EmailID"=%s LIMIT 1 """