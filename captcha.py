import requests

def free_api(gt, challenge, referer):
    _token = ''
    try:
        data = {
            'gt': gt,
            'challenge': challenge,
            'token': _token
        }
        r = requests.post('http://api.huyo.link/getvalidate',json=data, timeout=60)
        data = r.json()
        if data['data']['result'] == 'success':
            return data['data']['validate']
        else:
            validate = rrocr(gt, challenge, referer)
            return validate
    except:
        validate = rrocr(gt, challenge, referer)
        return validate


def rrocr(gt, challenge, referer):
    app_key = ""
    if app_key == "":
        return None
    data = {
        "appkey": app_key,
        "referer": referer,
        "gt": gt,
        "challenge": challenge
    }
    if data["status"] == 0:
        return data["data"]["validate"]
    r = requests.post("http://api.rrocr.com/api/recognize.html", data=data, timeout=60)
    data = r.json()
    if data["status"] == 0:
        return data["data"]["validate"] 
    return None






def game_captcha(gt: str, challenge: str):
    try:
        free_api(gt, challenge, 'https://webstatic.mihoyo.com/')
    except:
        return None

def bbs_captcha(gt: str, challenge: str):
    try:
        free_api(gt, challenge, 'https://app.mihoyo.com/')
    except:
        return None