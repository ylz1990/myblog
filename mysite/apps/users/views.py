import json
from django.shortcuts import render,redirect,reverse
from django.views import View

from django.contrib.auth import login,logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from users.forms import  RegisterForm,LoginForm
from users.models import Users

from utils.json_fun import to_json_data
from utils.res_code import Code, error_map

# Create your views here.


# 类视图  注册页面
class RegisterView(View):
    """
    /register/
    """
    def get(self,request):
        return render(request, "users/register.html")

    # 注册功能
    #  参数 : 用户名, 密码, 确认密码, 手机号, 短信验证码
    #  请求方式: POST
    #  提交: form,  ajax
    #  获取, 校验

    #  步骤:
    def post(self,request):
        #  1. 获取参数
        json_data = request.body   # byte  str
        if not json_data:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        #  2. 校验参数
        form = RegisterForm(data=dict_data)
        if form.is_valid():
            #  3. 存入数据到数据
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')

            user = Users.objects.create_user(username=username,password=password,mobile=mobile)
            login(request,user)
            #  4. 返回给前端
            return to_json_data(errmsg='恭喜您,注册成功!')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

# 参数, 登录账号, 密码, 记住
# 校验: 账号,账号格式, 是否为空, 账号和密码 数据库
# 请求方式: POST
# 提交 ajax

class LoginView(View):
    """"""
    # @method_decorator(ensure_csrf_cookie)
    def get(self,request):
        return render(request,'users/login.html')

    def post(self,request):
        # 1.获取参数
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf-8'))
        # 2.校验
        form = LoginForm(data=dict_data,request=request)   # 类的实例化
        # 3.返回给前端
        if form.is_valid():
            return to_json_data(errmsg='恭喜您,登录成功!')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# cookie session



class LogoutView(View):
    """"""
    def get(self,request):
        logout(request)
        return redirect(reverse('users:login'))

