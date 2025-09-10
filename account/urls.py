from tkinter.font import names

from account import views
from django.urls import path

urlpatterns = [
    path('login_page/',views.login_page,name="login_page"),
    path('register_page/',views.register_page,name="register_page"),
    path('send_otp/<email>/',views.send_otp , name="send_otp"),
    path('verify-otp/<email>/',views.verify_otp , name="verify_otp"),
    path('verify-account/<token>/',views.verify_email_token , name="verify_email_token"),
    path('login_vendor/' , views.login_vendor, name='login_vendor'),

    path('register_vendor/' , views.register_vendor, name='register_vendor'),
]