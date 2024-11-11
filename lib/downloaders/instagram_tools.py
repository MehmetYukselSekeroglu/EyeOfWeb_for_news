import requests
import json
from bs4 import BeautifulSoup
#from .. user_agent_tools import randomUserAgent

INSTAGRAM_BASE_DOMAIN = "https://instagram.com/"

def profile_link(username:str) -> str:
    return INSTAGRAM_BASE_DOMAIN + username

#
# json_data = json_data["require"][0][3][0]["__bbox"]["define"]
# index 156 | HEsap Bilgileri
#   içerisindekiler 
#       index 0: bilgi
#       index 1: boş
#       index 3: dict
#                   |-> içerisindekiler 
# {'ACCOUNT_ID': '0', 'USER_ID': '0', 'NAME': '', 'SHORT_NAME': None, 'IS_BUSINESS_PERSON_ACCOUNT': False,
#   'HAS_SECONDARY_BUSINESS_PERSON': False,
#   'IS_FACEBOOK_WORK_ACCOUNT': False, 'IS_INSTAGRAM_BUSINESS_PERSON': False,
#   'IS_MESSENGER_ONLY_USER': False, 'IS_DEACTIVATED_ALLOWED_ON_MESSENGER': False, 
#   'IS_MESSENGER_CALL_GUEST_USER': False, 'IS_WORK_MESSENGER_CALL_GUEST_USER': False,
#   'IS_WORKROOMS_USER': False, 'APP_ID': '936619743392459',
#   'IS_BUSINESS_DOMAIN': False, 'NON_FACEBOOK_USER_ID': '0', 'IS_INSTAGRAM_USER': 1, 
# 'IG_USER_EIMU': '0'}
#


import time
def get_profile_pic_url(username:str, **kwargs) -> tuple:
    
    try:

        profileRequests = requests.get(url=profile_link(username=username), **kwargs)

        if not profileRequests.ok:
            return (False, f"response status code: {profileRequests.status_code}")

        soup_data = BeautifulSoup(profileRequests.text, "html.parser")
        script_data = soup_data.find_all("script")
        for single_script in script_data:
            content_is = single_script.get_text()
            if "profile_pic_url" in content_is:
                json_data = json.loads(content_is)
                json_data = json_data["require"][0][3][0]["__bbox"]["require"][3][3][0]["initialRouteInfo"]
                profile_pic_url = json_data["route"]["rootView"]["props"]["profile_pic_url"]

        return (True, profile_pic_url)

    except Exception as err:
        return (False, err)


if __name__ == "__main__":
    
    curretnUserName = "mehmet_skroglu"
     
    r_args = {
        "headers":{
            "User-Agent":"sea",
        },
        "timeout":10
    }
    
    
    profilePicUrl = get_profile_pic_url(curretnUserName, **r_args)
    print(profilePicUrl)