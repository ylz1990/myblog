from django.shortcuts import render
# 导入 验证码  py
from utils.captcha.captcha import captcha

from django.http import HttpResponse
from django.views import View

# Create your views here.


class ImageCode(View):
    """
    /image_code
    """
    def get(self,request,image_code_id):
        # 将图形验证码分为文字和图片 分别取出
        text,image = captcha.generate_captcha()
        # content_type="image/jpg"  指定图片类型jpg
        return HttpResponse(content=image, content_type="image/jpg")
