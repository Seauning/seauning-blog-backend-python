"""
生产者
    # 下面即是我们的任务（发送短信验证码）
    @app.task
    def celerySendSmsCode(phone, smsCode):
        # 3.发送短信验证码
        sdk = SmsSDK(ytx.accId, ytx.accToken, ytx.appId)
        sdk.sendMessage("1", phone, (smsCode, 5))
消费者
    在虚拟环境下执行指令
    celery -A celery实例的脚本路径 worker -l info
队列（中间人、经纪人）
    设置broker(通过加载配置文件设置)
    app.config_from_object('celeryTask.config')
    '''
        项目中指定redis作为中间人
    '''
    brokerUrl = 'redis://127.0.0.1:6379/15'
Celery -- 3者的实现
"""
# 1、设置celery在django运行的环境
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_server.settings')

# 2、创建celery实例
from celery import Celery
# 参数：
#     main: 脚本路径
app = Celery('celeryTask')

# 3、设置broker(通过加载配置文件设置)
app.config_from_object('celeryTask.config')

# 4、celer自动检测包
app.autodiscover_tasks(['celeryTask.sms'])
