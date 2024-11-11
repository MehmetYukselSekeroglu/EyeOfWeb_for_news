CREATE TABLE IF NOT EXISTS "ImageBasedMain" (
    "ID"            SERIAL PRIMARY KEY,
    "BaseDomainID"  INT NOT NULL, 
    "BaseUrlPathID" INT NOT NULL, 
    "BaseUrlEtcID"  INT NOT NULL,
    "ImageDomainID" INT DEFAULT NULL,
    "ImagePathID"   INT DEFAULT NULL,
    "ImageUrlEtcID" INT DEFAULT NULL,
    "ImageTitleID"  INT DEFAULT NULL,
    "ImageID"       INT DEFAULT NULL,
    "FaceID"        INT[] DEFAULT NULL,
    "CategoryID"    SMALLINT DEFAULT NULL,
    "HashID"        INT NOT NULL,   
    "PhoneID"       INT DEFAULT NULL,
    "EmailID"       INT DEFAULT NULL,  
    "Date" TIMESTAMP DEFAULT NOW()

);


CREATE TABLE IF NOT EXISTS "PageBasedMain" (
    "ID"            SERIAL PRIMARY KEY,
    "BaseDomainID"  INT NOT NULL, 
    "UrlPathID"     INT NOT NULL, 
    "BaseUrlEtcID"  INT NOT NULL,
    "CategoryID"    SMALLINT DEFAULT NULL,
    "PhoneID"       INT[] DEFAULT NULL,
    "EmailID"       INT[] DEFAULT NULL,
    "Date" TIMESTAMP DEFAULT NOW()

);

CREATE TABLE IF NOT EXISTS "FaceStorageID" (
    "ID"                SERIAL PRIMARY KEY,
    "FaceEmbeddingData" BYTEA NOT NULL,
    "Landmarks2d"       BYTEA NOT NULL,
    "FaceBox"           BYTEA NOT NULL,
    "DetectionScore"    FLOAT NOT NULL,
    "FaceGender"        BOOLEAN DEFAULT NULL,
    "FaceAge"           SMALLINT DEFAULT NULL,
    "DetectionDate"     TIMESTAMP DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS "ImageStorageID" (
    "ID"            SERIAL PRIMARY KEY,
    "BinaryImage"   BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS "UrlPathID" (
    "ID"        SERIAL PRIMARY KEY,
    "Path"      VARCHAR(1000) NOT NULL
);

CREATE TABLE IF NOT EXISTS "ImageTitleID" (
    "ID"        SERIAL PRIMARY KEY,
    "Title"      VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS "ImageUrlPathID" (
    "ID"        SERIAL PRIMARY KEY,
    "Path"      VARCHAR(1000) NOT NULL
);

CREATE TABLE IF NOT EXISTS "UrlEtcID" (
    "ID"        SERIAL PRIMARY KEY,
    "Etc"      VARCHAR(1000) NOT NULL
);

CREATE TABLE IF NOT EXISTS "ImageUrlEtcID" (
    "ID"        SERIAL PRIMARY KEY,
    "Etc"      VARCHAR(1000) NOT NULL
);

CREATE TABLE IF NOT EXISTS "BaseDomainID" (
    "ID"        SERIAL PRIMARY KEY,
    "Domain"    VARCHAR (150) NOT NULL
);

CREATE TABLE IF NOT EXISTS "PhoneNumberID"(
    "ID"            SERIAL PRIMARY KEY,
    "PhoneNumber"   VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS "EmailAddressID"(
    "ID"            SERIAL PRIMARY KEY,
    "EmailAddress"  VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS "ImageHashID" (
    "ID"            SERIAL PRIMARY KEY,
    "ImageHash"     VARCHAR(40), 
    "DetectionDate" TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "WebSiteCategoryID"(
    "ID"        SERIAL PRIMARY KEY,
    "Category"  VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS "CrawledAddress" (
    "ID"            SERIAL PRIMARY KEY,
    "BaseDomain"    VARCHAR(300) NOT NULL, 
    "BaseUrlPath"   VARCHAR(1000) DEFAULT NULL, 
    "BaseUrlEtc"    VARCHAR(1000) DEFAULT NULL,   
    "CrawlDate"     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "DefaultTargetList"(
    "ID"            SERIAL PRIMARY KEY,
    "Url"           TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "DbInfo" (
    "ID"            SERIAL PRIMARY KEY,
    "key"           TEXT NOT NULL UNIQUE,
    "val"           BOOLEAN NOT NULL
);






--- Creating Index's




--- index fo image based 
CREATE INDEX "BaseDomID_index" ON "ImageBasedMain" ( "BaseDomainID" );
CREATE INDEX "BaseUrlID_index" ON "ImageBasedMain" ( "BaseUrlPathID" );
CREATE INDEX "BaseUrlEtcID_index" ON "ImageBasedMain" ( "BaseUrlEtcID" );
CREATE INDEX "ImageDomID_index" ON "ImageBasedMain" ( "ImageDomainID" );
CREATE INDEX "ImagePathID_index" ON "ImageBasedMain" ( "ImagePathID" );
CREATE INDEX "ImageUrlEtcID_index" ON "ImageBasedMain" ( "ImageUrlEtcID" );
CREATE INDEX "ImageTitleID_index" ON "ImageBasedMain" ( "ImageTitleID" );
CREATE INDEX "ImageID_index" ON "ImageBasedMain" ( "ImageID" );
CREATE INDEX "FaceID_index" ON "ImageBasedMain" ( "FaceID" );
CREATE INDEX "CategoryID_index" ON "ImageBasedMain" ( "CategoryID" );
CREATE INDEX "HashID_index" ON "ImageBasedMain" ( "HashID" );
CREATE INDEX "PhoneID_index" ON "ImageBasedMain" ( "PhoneID" );
CREATE INDEX "EmailID_index" ON "ImageBasedMain" ( "EmailID" );
--- index for PageBased
CREATE INDEX "BaseDomID_PageBasedMain_index" ON "PageBasedMain" ( "BaseDomainID" );
CREATE INDEX "BaseUrlID_PageBasedMain_index" ON "PageBasedMain" ( "UrlPathID" );
CREATE INDEX "BaseUrlEtcID_PageBasedMain_index" ON "PageBasedMain" ( "BaseUrlEtcID" );
CREATE INDEX "CategoryID_PageBasedMain_index" ON "PageBasedMain" ( "CategoryID" );
CREATE INDEX "PhoneID_PageBasedMain_index" ON "PageBasedMain" ( "PhoneID" );
CREATE INDEX "EmailID_PageBasedMain_index" ON "PageBasedMain" ( "EmailID" );
CREATE INDEX "idx_UrlPathID_index" ON "UrlPathID" ( "ID" );
CREATE INDEX "Path_UrlPathID_index" ON "UrlPathID" ( "Path" );
CREATE INDEX "idx_ImageTitleID_index" ON "ImageTitleID" ( "ID" );
CREATE INDEX "Title_ImageTitleID_index" ON "ImageTitleID" ( "Title" );
CREATE INDEX "idx_ImageUrlPathID_index" ON "ImageUrlPathID" ( "ID" );
CREATE INDEX "Path_ImageUrlPathID_index" ON "ImageUrlPathID" ( "Path" );
CREATE INDEX "idx_UrlEtcID_index" ON "UrlEtcID" ( "ID" );
CREATE INDEX "Etc_UrlEtcID_index" ON "UrlEtcID" ( "Etc" );
CREATE INDEX "idx_ImageUrlEtcID_index" ON "ImageUrlEtcID" ( "ID" );
CREATE INDEX "Etc_ImageUrlEtcID_index" ON "ImageUrlEtcID" ( "Etc" );
CREATE INDEX "idx_BaseDomainID_index" ON "BaseDomainID" ( "ID" );
CREATE INDEX "Domain_BaseDomainID_index" ON "BaseDomainID" ( "Domain" );
CREATE INDEX "idx_PhoneNumberID_index" ON "PhoneNumberID" ( "ID" );
CREATE INDEX "PhoneNumber_PhoneNumberID_index" ON "PhoneNumberID" ( "PhoneNumber" );
CREATE INDEX "idx_EmailAddressID_index" ON "EmailAddressID" ( "ID" );
CREATE INDEX "EmailAddress_EmailAddressID_index" ON "EmailAddressID" ( "EmailAddress" );
CREATE INDEX "idx_ImageHashID_index" ON "ImageHashID" ( "ID" );
CREATE INDEX "ImageHash_ImageHashID_index" ON "ImageHashID" ( "ImageHash" );
CREATE INDEX "idx_WebSiteCategoryID_index" ON "WebSiteCategoryID" ( "ID" );
CREATE INDEX "idx_CrawledAddress_index" ON "CrawledAddress" ( "ID" );
CREATE INDEX "BaseDomainID_CrawledAddress_index" ON "CrawledAddress" ( "BaseDomain" );
CREATE INDEX "BaseUrlPathID_CrawledAddress_index" ON "CrawledAddress" ( "BaseUrlPath" );
CREATE INDEX "BaseUrlEtcID_CrawledAddress_index" ON "CrawledAddress" ( "BaseUrlEtc" );


CREATE INDEX "idx_DefaultTargetList_index" ON "DefaultTargetList" ( "ID" );
CREATE INDEX "Url_DefaultTargetList_index" ON "DefaultTargetList" ( "Url" );



--- insert defaults value's 



INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('news');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('education');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('tech');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('health');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('sports');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('arts');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('finance');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('travels');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('government');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('military');
INSERT INTO "WebSiteCategoryID" ( "Category" ) VALUES ('space');