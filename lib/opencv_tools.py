import cv2
import json


def export_kps_as_json(kps:tuple) -> list:
    return_list = []
    
    for single in kps:
        single:cv2.KeyPoint
        
        return_list.append({
            "pt":single.pt,
            "size":single.size,
            "angle":single.angle,
            "response":single.response,
            "octave":single.octave,
            "class_id":single.class_id
            })
    
    return json.dumps(return_list)
        