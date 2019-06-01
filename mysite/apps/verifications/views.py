from django.shortcuts import render
# 导入 验证码  py
from utils.captcha.captcha import captcha
from django.http import HttpResponse,JsonResponse
from django.views import View
# 导入django_redis
from django_redis import get_redis_connection
# 导入固定的值
from verifications import constants
# 导入日志器
import  logging
import json
import random
import string
# 导入数据库
from users import models
from utils.json_fun import to_json_data
from utils.res_code import Code,error_map
from utils.yuntongxun.sms import CCP
from verifications.forms import CheckImgCodeForm

# 导入日志器
logger = logging.getLogger('django')

# 验证码
class ImageCode(View):
    """
    /image_code
    """
    def get(self,request,image_code_id):
        # 将图形验证码分为文字和图片 分别取出
        text,image = captcha.generate_captcha()
        # 连接 验证码redis数据库
        con_redis = get_redis_connection(alias="verify_codes")
        # 设置uuid 作为键
        img_key = 'img_{}'.format(image_code_id)
        # 存入数据库 键  时间  值
        con_redis.setex(img_key,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        # 用日志器 打印验证码信息
        logger.info("Image_code: {}".format(text))
        # content_type="image/jpg"  指定图片类型jpg
        return HttpResponse(content=image, content_type="image/jpg")

class CheckUsernameView(View):
    """
    /usernames/(?P<username>\w{5,20})/
    """
    def get(self,request,username):

        # 到数据库查询用户名是否存在 filter,  查找用户名个数
        count = models.Users.objects.filter(username=username).count()
        data = {
           "count":count,
           "username":username
        }
        return to_json_data(data=data)
        # return JsonResponse({'data':data})

# 验证手机号码
class CheckMobileView(View):
    """
    /mobiles/(?P<mobile>1[3-9]\d{0})/
    """
    def get(self,request,mobile):

        # 到数据库查询用户名是否存在 filter,  查找用户名个数
        count = models.Users.objects.filter(mobile=mobile).count()
        data = {
           "count":count,
           "mobile":mobile
        }
        return to_json_data(data=data)



# 手机 :  不为空, 手机号格式, 手机号注册过
# 验证码:  不为空, 与数据库中存入的数据
# uuid : 格式
class SmsCodesView(View):
    """
    /sms_codes/
    """
    def post(self,request):
        # 1. 获取参数
        json_data = request.body   # byte  str
        if not json_data:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        # 2. 验证参数
        form = CheckImgCodeForm(data=dict_data)
        if form.is_valid():
            # 3.保存短信
            mobile = form.cleaned_data.get('mobile')
            # sms_num = ''
            # for i in range(6):
            #     sms_num += random.choice(string.digits)
            sms_num = ''.join([random.choice(string.digits) for _ in range(constants.SMS_CODE_NUMS)])
            con_redis = get_redis_connection(alias='verify_codes')

            pl = con_redis.pipeline()

            sms_text_fmt = 'sms_{}'.format(mobile)   # 验证码的键
            sms_flg_fmt = 'sms_flag_{}'.format(mobile)   # 发送标记
            try:
                pl.setex(sms_flg_fmt,constants.SEND_SMS_CODE_INTERVAL,constants.SMS_CODE_TEMP_ID)
                pl.setex(sms_text_fmt,constants.SMS_CODE_REDIS_EXPIRES,sms_num)
                pl.execute()
            except Exception as e:
                logger.debug("redis 执行异常: {}".format(e))
                return to_json_data(errno=Code.UNKOWNERR,errmsg=error_map[Code.UNKOWNERR])
            # 4. 发送短信验证码
            logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            # 发送短语验证码
            # try:
            #     result = CCP().send_template_sms(mobile,
            #                                      [sms_num, constants.SMS_CODE_REDIS_EXPIRES],
            #                                      constants.SMS_CODE_TEMP_ID)
            # except Exception as e:
            #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            #         return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            #     else:
            #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
    # 5. 返回给前端
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)