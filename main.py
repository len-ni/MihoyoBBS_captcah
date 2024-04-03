import onnxruntime as ort
import numpy as np
from PIL import Image
import requests
import time
import re
import json
import os
import random
import string
from loguru import logger
from io import BytesIO
import execjs

'''
加密，识别参数并未开源
headers一处需要更改
'''

headers = {}
model_path = ''

b9 = [(0,0,113,113), (115,0,228,113), (231,0,344,113), 
      (0,115,113,228), (115,115,228,228), (231,115,344,228), 
      (0,231,113,344), (115,231,228,344), (231,231,344,344)]   # 九张图片的坐标
p1 = (0,344,45,384)   # 单张图片坐标
correspond = ['1_1,', '2_1,', '3_1,', '1_2,', '2_2,', '3_2,' ,'1_3,', '2_3,', '3_3,']   # 某验需要的结果

def run_js_function_with_execjs(js_file_path, function_name, *args):
    # 调用js获取加密参数
    with open(js_file_path, 'r') as js_file:
        js_code = js_file.read()
    ctx = execjs.compile(js_code)
    result = ctx.call(function_name, *args)
    return result

def ocr(image):
    # ocr识别验证码
    image = image.convert("RGB")
    model = ort.InferenceSession(model_path)
    def crop_funcaptcha_ans_image(image, box):
        return image.crop(box)
    
    def process_pair_classifier_ans_image(image, box, input_shape=(32, 32)):
        sub_image = crop_funcaptcha_ans_image(image, box).resize(input_shape)
        return np.array(sub_image).transpose(2, 0, 1)[np.newaxis, ...] / 255.0
    
    def run_prediction(output_names, input_feed):
            return model.run(output_names, input_feed)

    left = process_pair_classifier_ans_image(image, p1)
    true1 = []
    for i, box in enumerate(b9):
        right = process_pair_classifier_ans_image(image, box)
        prediction = run_prediction(None, {'input_left': left.astype(np.float32),
                                                    'input_right': right.astype(np.float32)})[0]
        prediction_value = prediction[0][0]
        formatted_value = "{:.5f}".format(prediction_value)
        numeric_value = float(formatted_value)
        if numeric_value > 0.6:
            true1.append(i)
        logger.info(f'图片{i}   概率{formatted_value}')
    logger.info(true1)
    return true1

def get_result(shibie):
    # 识别结果转为某验需要的
    result = ''
    for i in shibie:
        result = result + result[i]
    return result[:-1]

def geetest_run(gt, challenge):
    global headers

    # 三次请求（点击验证码等...................）
    requests.get('https://api.geetest.com/gettype.php', params={'gt': gt,'callback': f'geetest_{str(int(time.time() * 1000))}'}, headers=headers)
    requests.get(f'https://api.geetest.com/get.php?gt={gt}&challenge={challenge}&lang=zh-cn&pt=0&client_type=web&callback=geetest_{str(int(time.time() * 1000))}',headers=headers,)
    requests.get(f'https://api.geevisit.com/ajax.php?gt={gt}&challenge={challenge}&lang=zh-cn&pt=0&client_type=web&callback=geetest_{str(int(time.time() * 1000))}',headers=headers,)

    # 请求图片等参数
    params = {
        'is_next': 'true',
        'type': 'click',
        'gt': gt,
        'challenge': challenge,
        'lang': 'zh-cn',
        'https': 'false',
        'protocol': 'https://',
        'offline': 'false',
        'product': 'embed',
        'api_server': 'api.geevisit.com',
        'isPC': 'true',
        'autoReset': 'true',
        'width': '100%',
        'callback': f'geetest_{str(int(time.time() * 1000))}',
    }
    response = requests.get('https://api.geevisit.com/get.php', params=params, headers=headers)
    match = re.match(r'geetest_\d+\((.*)\)', response.text)
    if match:
        json_data = match.group(1)
        data = json.loads(json_data)
        pic = data['data']['pic']
        s = data['data']['s']
        c = data['data']['c']

        rs = requests.get(f'https://static.geetest.com{pic}',params={'challenge': challenge,},)
        hash_value = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        with open(os.path.join('save', hash_value + '.jpg'), 'wb') as f:
            f.write(rs.content)
        image = Image.open(BytesIO(rs.content))
        _ocr = ocr(image)
        # opts, tm, ca , passtime = runguiji(shibie)    # 轨迹参数等，算法不开源
        # get_result(shibie)是需要的结果 pic图片链接(上一请求返回) c参数(上一请求返回) s参数(上一请求返回) gt参数(某验id) challenge参数(流水号) opts轨迹 passtime完成时间 ca一个没用的参数 json.dumps(tm)一个没用的参数
        # w = run_js_function_with_execjs('m4.js', 'get_w', get_result(shibie), pic, c, s, gt, challenge, opts, passtime, ca, json.dumps(tm))   # 加密w逆向，逆向不开源
        headers = {}
        params = {
            'gt': gt,
            'challenge': challenge,
            'lang': 'zh',
            'pt': '0',
            'client_type': 'web',
            'w': 'w',   #此处是加密的 w
            'callback': f'geetest_{str(int(time.time() * 1000))}',
        }
        time.sleep(1)
        response = requests.get('https://api.geevisit.com/ajax.php',headers=headers,params=params)
        match = re.match(r'geetest_\d+\((.*)\)', response.text)
        if match:
            json_data = match.group(1)
            data = json.loads(json_data)
            logger.info(data)