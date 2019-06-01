from django import forms
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from users.models import Users

# 创建手机号的正则校验器
mobile_validator = RegexValidator(r"^1[3-9]\d{9}$", "手机号码格式不正确")



class CheckImgCodeForm(forms.Form):
    """

    """
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    text = forms.CharField(max_length=4, min_length=4,
                           error_messages={"min_length": "图片验证码长度有误", "max_length": "图片验证码长度有误",
                                           "required": "图片验证码不能为空"})
    def clean(self):
        clean_data = super().clean()
        mobile_num = clean_data.get('mobile')
        image_text = clean_data.get('text')   # 用户输入的图形验证码
        image_uuid = clean_data.get('image_code_id')

        if Users.objects.filter(mobile=mobile_num):
            raise forms.ValidationError("手机号已经注册,请重新输入!")

        con_redis = get_redis_connection(alias='verify_codes')
        img_key =  'img_{}'.format(image_uuid)
        real_image_code_origin = con_redis.get(img_key)  # redis当中取出来的bytes
        # if real_image_code_origin:
        #     real_image_code = real_image_code_origin.decode('utf-8')
        # else:
        #     real_image_code = None
        real_image_code = real_image_code_origin.decode('utf-8')  if real_image_code_origin else None    # 数据库取出来的的图形码
        con_redis.delete(img_key)

        if (not real_image_code) or (image_text != real_image_code):  #或者
            raise forms.ValidationError('图形验证失败!')

        # 60 秒  检查是否在60 内
        # 构建 键, 从redis
        sms_flg_fmt = 'sms_flag_{}'.format(mobile_num)
        sms_flg = con_redis.get(sms_flg_fmt)
        if sms_flg:
            raise forms.ValidationError('获取手机短信验证码过于频繁')












