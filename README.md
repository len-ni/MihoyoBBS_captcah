# geetest3_captcah九宫格模型

##使用方法

用于[MihoyoBBSTools](https://github.com/Womsxd/MihoyoBBSTools)的游戏签到的免费验证码解决API

仅用于九宫格验证码，正确率自测，不低于百分之60.

为限制每人使用次数token从 https://t.me/nc_token_bot 获取完全免费。每人每天6次识别正确数。


post传参
API地址 http://api.huyo.link/getvalidate
需要参数 gt  challenge  token

请将timeout时间设置为60！！！，api如果识别错误会重试3次！！！

main.py是开源除模型，逆向的其他请求逻辑
