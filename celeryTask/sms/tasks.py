# 生产者 -- 任务 ， 函数
# 1、这个函数必须要让celery的实例的task装饰器装饰
# 2、需要celery自动检测指定包的任务
from ronglian_sms_sdk import SmsSDK
from libs import yuntongxin as ytx
from celeryTask.celery import app
import logging
logger = logging.getLogger('django')


# 下面即是我们的任务（发送短信验证码）
@app.task(name='celerySendSmsCode')
def celerySendSmsCode(phone, smsCode):
    # 3.发送短信验证码
    try:
        sdk = SmsSDK(ytx.accId, ytx.accToken, ytx.appId)
        sdk.sendMessage("1", phone, (smsCode, 5))
    except Exception as e:
        logger.error(e)
