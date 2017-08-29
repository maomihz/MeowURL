# geetest interface

import json

from meowurl import app
from geetest import GeetestLib as Geetest

def reg():
    if not "CAPTCHA_GEETEST" in app.config:
        raise Exception("no configuration for geetest captcha")
    
    gt = Geetest(*app.config["CAPTCHA_GEETEST"])
    not_offline = gt.pre_process()
    
    # hope this is json
    resp = gt.get_response_str()
    obj = json.loads(resp)
    
    obj["offline"] = not not_offline
    obj["gt"] = obj["gt"]
    obj["challenge"] = obj["challenge"]
    
    return obj
    
def verify(challenge, validate, seccode, offline=0):
    if not "CAPTCHA_GEETEST" in app.config:
        return True
    
    gt = Geetest(*app.config["CAPTCHA_GEETEST"])
    
    result = (gt.success_validate if not offline else gt.failback_validate) \
             (challenge, validate, seccode)
    
    return bool(result)
