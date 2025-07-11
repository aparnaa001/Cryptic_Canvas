"""
URL configuration for Steganography project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Steganoapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('register',views.registration),
    path('userhome',views.userhome),
    path('adminhome',views.adminhome),
    path('encrypt',views.encrypt),
    path('userhome',views.userhome),
    path('decrypt',views.decrypt),
    path('userhistory',views.userhistory),
    path('feedback',views.feedback),
    path('adminfeedback',views.adminfeedback),
    path('usrerview',views.userview),
    path('userlist',views.userlist),
    path('toggleuser',views.toggleuser),
    path('userprofile',views.userprofile),

    
]
