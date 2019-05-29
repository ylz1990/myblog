from django.shortcuts import render
from django.views import View
# Create your views here.


# 类视图  注册页面
class RegisterView(View):
    """
    /register/
    """
    def get(self,request):
        return render(request, "users/register.html")
