import flask
from werkzeug.utils import secure_filename
import imghdr
import os
import cv2
import base64
from timeit import default_timer
import psycopg2.extras
import psycopg2
from lib.opencv_draw                          import landmarks_rectangle
from lib.init_insightface                     import initilate_insightface
from lib.load_config                          import load_config_from_file
from lib.numpy_tools                          import buffer2numpy_float32, compute_cosine_sim, load_ImageFromContext,buffer2numpy_uint8
from lib.downloaders.imageFromUrl             import get_ImageFromUrl
import instaloader
from lib.downloaders.imageFromUrl             import downloadImage_defaultSafe
from waitress import serve



CONFIG = load_config_from_file()
UPLOAD_DIR = "api_temp"
SEARCH_API = "/search"
INFO_API = "/info"
RETURN_IMG_FORMAT = ".png"

if CONFIG[1]["api_config"]["localhost_only"]:
    API_HOST = "127.0.0.1"
else:
    API_HOST = "0.0.0.0"

if CONFIG[1]["api_config"]["port"]:
    API_PORT = int(CONFIG[1]["api_config"]["port"])
else:
    API_PORT = 8080
    
insightfaceApp = initilate_insightface(main_conf=CONFIG)
instaController = instaloader.Instaloader()


EXCLUDED_DOMAINS_FOR_DOWNLOAD = ["instagram.com",]

def connectDatabase() -> psycopg2.extensions.connection:
    return psycopg2.connect(**CONFIG[1]["database_config"])

def releaseConnection(db_conn:psycopg2.extensions.connection,db_cursor:psycopg2.extensions.cursor) -> None:
    db_cursor.close()
    db_conn.close()

def validate_image(stream_of_image):
    header_is = stream_of_image.read(512)
    file_format = imghdr.what(None, header_is)
    if not file_format:
        return None
    return "." + str(file_format)



ApiApp = flask.Flask(__name__)

ApiApp.config["MAX_CONTENT_LENGTH"] = (1024*1024) * 7 # 7mb upload limits
ApiApp.config["UPLOAD_EXTENSIONS"] = [".png",".jpg",".wepm", ".jpeg"] # Accept only this extensions 
ApiApp.config["UPLOAD_PATH"] = UPLOAD_DIR # set upload dir 


# Get system latest information via api 
# route /info methods: get
# counting database * 

@ApiApp.route("/info", methods=["GET"])
def system_information():
    db = connectDatabase()
    db_cursor = db.cursor()
    
    
    STATIC_COMBINATION_COUNT = """SELECT COUNT(*) FROM "ImageBasedMain" """
    STATIC_FACES_COUNT = """SELECT COUNT(*) FROM "FaceStorageID" """
    STATIC_EMAIL_COUNT = """SELECT COUNT(*) FROM "EmailAddressID" """
    STATIC_DOMAIN_COUNT = """SELECT COUNT(*) FROM "BaseDomainID" """
    STATIC_HASH_COUNT = """SELECT COUNT(*) FROM "ImageHashID" """
    STATIC_URLPATH_COUNT = """SELECT COUNT(*) FROM "UrlPathID" """
    STATIC_URLETC_COUNT = """SELECT COUNT(*) FROM "UrlEtcID" """
    
    db_cursor.execute(STATIC_COMBINATION_COUNT)
    totalCombination = db_cursor.fetchall()[0][0]
    
    db_cursor.execute(STATIC_FACES_COUNT)
    totalFaces = db_cursor.fetchall()[0][0]
    
    db_cursor.execute(STATIC_EMAIL_COUNT) 
    totalEmail = db_cursor.fetchall()[0][0]
    
    db_cursor.execute(STATIC_DOMAIN_COUNT)
    totalDomain = db_cursor.fetchall()[0][0]

    db_cursor.execute(STATIC_HASH_COUNT)
    totalImageHash = db_cursor.fetchall()[0][0]

    db_cursor.execute(STATIC_URLPATH_COUNT)
    totalUrlPath = db_cursor.fetchall()[0][0]

    db_cursor.execute(STATIC_URLETC_COUNT)
    totalUrlPathEtc = db_cursor.fetchall()[0][0]

    return flask.jsonify({
        "success":True,
        "message":"Proccess successfuly",
        "domain_count":totalDomain,
        "face_count":totalFaces,
        "image_hash_count":totalImageHash,
        "email_count":totalEmail,
        "url_path_count":totalUrlPath,
        "url_pathetc_count":totalUrlPathEtc,
        "total_combination":totalCombination
    })
    
    
    

    
    
        
        
@ApiApp.route("/search", methods=["POST"])
def webeye_api():
    
    targetFile = flask.request.files["target"]
    
    if not targetFile:
        return flask.jsonify({
            "success":False,
            "message":"No target selected"
        })

    safe_filename = secure_filename(targetFile.filename)
    
    if safe_filename == "":
        return flask.jsonify({
            "success":False,
            "message":"No target selected"
        })
        
    file_extensions = os.path.splitext(safe_filename)
    if len(file_extensions) != 2:
        return flask.jsonify({
            "success":False,
            "message":"File is not safe, access denied!"
        })
    
    file_extensions = file_extensions[1]

    if file_extensions not in ApiApp.config["UPLOAD_EXTENSIONS"] or file_extensions != validate_image(targetFile.stream):
        return flask.jsonify({
            "success":False,
            "message":"File is not safe, access denied!"
        })

    #cv2_image = targetFile.stream.read()

    targetFile.stream.seek(0)
    cv2_image = load_ImageFromContext(targetFile.stream.read())
    
    
    
    detectedFaces = insightfaceApp.get(cv2_image)
    
    if len(detectedFaces) != 1:
        return flask.jsonify({
            "success":False,
            "message":f"Only accepting 1 face in image but your image have {len(detectedFaces)} faces !"
        })
        
    sourceEmbedding = detectedFaces[0]["embedding"]

    db = connectDatabase()
    db_cursor = db.cursor()
    
    db_cursor.execute("""SELECT * FROM "FaceStorageID" """)

    MatchIDs = {}
    start_time = default_timer()
    
    
    
    while True:
    
        currentFace = db_cursor.fetchone()
    
        if currentFace == None:
            break
    
        _id = currentFace[0]
        _TargetEmbeds = buffer2numpy_float32(currentFace[1])
        _faceBox = currentFace[3]
        _detectionScore = currentFace[4]
        _faceGender     = currentFace[5]
        _faceAge        = currentFace[6]
        _detectionDate  = currentFace[7]

        _similarity = compute_cosine_sim(sourceEmbedding,_TargetEmbeds)

        if float(_similarity * 100) > float(35):
            MatchIDs[float(_similarity * 100)] = {
                "id":_id,
                "bbox":_faceBox,
                "detection_score":_detectionScore,
                "age":_faceAge,
                "gender":_faceGender,
                "detection_date":_detectionDate
            } 
    
    
        
    if len(MatchIDs) < 1:
        return flask.jsonify({
            "success":True,
            "message":"Proccess successfuly but no similar face found",
            "took":None,
            "data":[]   
    })
    
    print(f"-INFO-: TOTAL RESULTS: {len(MatchIDs)}")
    similarity_higger_list = list(MatchIDs.keys())
    similarity_higger_list.sort(reverse=True)
    return_data_list = []
    
    
    
    limit_checker = 0
    for higger_sim in similarity_higger_list:
        """
        #! Reference
                "id":_id,
                "detection_score":_detectionScore,
                "age":_faceAge,
                "gender":_faceGender,
                "detection_date":_detectionDate
        """        
        
        
        key = MatchIDs[higger_sim]["id"]
        _faceBox = MatchIDs[higger_sim]["bbox"]
        _detScore = MatchIDs[higger_sim]["detection_score"]
        _age =MatchIDs[higger_sim]["age"]
        _gender = MatchIDs[higger_sim]["gender"]
        _d_date = MatchIDs[higger_sim]["detection_date"]
        
        db_cursor.execute("""SELECT * FROM "ImageBasedMain" WHERE %s=ANY("FaceID") """,(int(key),))
        results_is = db_cursor.fetchall()[0]

        db_id = results_is[0]
        baseDomID = results_is[1]
        urlPathID = results_is[2]
        urlEtcID  = results_is[3]
        
        imgBaseDomID = results_is[4]
        imgPathID    = results_is[5]
        imgEtcID     = results_is[6]
        imgTitleID   = results_is[7]
        imgStorageID = results_is[8]
        faceID       = results_is[9]
        

        db_cursor.execute("""SELECT "Title" FROM "ImageTitleID" WHERE "ID"=%s""",(imgTitleID,))
        imgTitle = db_cursor.fetchall()[0][0]
        
        
        db_cursor.execute("""SELECT "Domain" FROM "BaseDomainID" WHERE "ID"=%s """, (baseDomID, ))
        baseDom = db_cursor.fetchall()[0][0]

        db_cursor.execute("""SELECT "Domain" FROM "BaseDomainID" WHERE "ID"=%s """, (imgBaseDomID, ))
        imgBaseDom = db_cursor.fetchall()[0][0]

        db_cursor.execute("""SELECT "Path" FROM "UrlPathID" WHERE "ID"=%s """, (urlPathID, ))
        urlPath = db_cursor.fetchall()[0][0]
        
        db_cursor.execute("""SELECT "Etc" FROM "UrlEtcID" WHERE "ID"=%s """, (urlEtcID, ))
        urlEtc = db_cursor.fetchall()[0][0]

        db_cursor.execute("""SELECT "Path" FROM "ImageUrlPathID" WHERE "ID"=%s """, (imgPathID, ))
        imgUrlPath = db_cursor.fetchall()[0][0]

        db_cursor.execute("""SELECT "Etc" FROM "ImageUrlEtcID" WHERE "ID"=%s """, (imgEtcID, ))
        imgUrlEtc = db_cursor.fetchall()[0][0]

        img_url =  "https://" + imgBaseDom + imgUrlPath 
        img_url_2 = "http://" + imgBaseDom + imgUrlPath         
        if imgUrlEtc:
            img_url += "?"+ imgUrlEtc
            img_url_2 += "?"+ imgUrlEtc

        img_url = str(img_url)

        if imgBaseDom not in EXCLUDED_DOMAINS_FOR_DOWNLOAD:        

            getImage = get_ImageFromUrl(img_url)
            if getImage[0] == False:
                getImage2 = get_ImageFromUrl(img_url_2)
                if getImage2[0] == False:
                    return_img = None
                else:
                    return_img = getImage2[1]
            else:
                return_img = getImage[1]

        elif  "instagram.com" in imgBaseDom:
            
            if True:
                
                return_img = None
            else:
                
                profileUsername = str(imgUrlPath).replace("/","")
                profileUsername = str(profileUsername)
                print("Resim alma öncesi")

                profile = instaloader.Profile.from_username(instaController.context, profileUsername)
                print("Resim alma işemi")
                getImage_insta = downloadImage_defaultSafe(profile.profile_pic_url)
                if getImage_insta[0] == False:
                    return_img = None
                else:
                    return_img = getImage_insta[1]
            
                            
        
        if return_img is not None:
            return_img = landmarks_rectangle(cv2_image=return_img,data_list=buffer2numpy_float32(_faceBox))
            _, return_img = cv2.imencode(RETURN_IMG_FORMAT, return_img)


        if return_img is None:
            return_img = cv2.imread(str(CONFIG[1]["base_dir"]+ "lib" + os.path.sep + "defaults" + os.path.sep + "none.png"))
            _, return_img = cv2.imencode(RETURN_IMG_FORMAT, return_img)

        if _gender:
            _gender = "Male"
        else:
            _gender = "Famale"
        
        
        return_img = base64.b64encode(return_img).decode("utf-8")
        

        return_data_list.append({
            "similarity":higger_sim,
            "deceted_url": "http://" + baseDom + "/"+ urlPath + urlEtc,
            "image_url":img_url,
            "age":_age,
            "gender":_gender,
            "detection_score":_detScore,
            "detection_date":_d_date,
            "image":return_img,
            "title":imgTitle
        })
        limit_checker += 1
        
        if limit_checker == 30:
            break
        
        

    stop_time = default_timer()
    return flask.jsonify({
            "success":True,
            "message":"Proccess successfuly",
            "took":stop_time-start_time,
            "data":return_data_list   
    })


serve(ApiApp,host=API_HOST, port=API_PORT)
