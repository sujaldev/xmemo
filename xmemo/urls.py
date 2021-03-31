"""xmemo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from cs.views import *
from physics.views import phy_view
from chemistry.views import chem_view
from mathematics.views import math_view
from english.views import eng_view

urlpatterns = [
    path("update-review/", update_question_review, name="update-review"),
    path("search-keyword/", display_by_key, name="search-keyword"),
    path('search/', display_by_date, name="search-date"),
    path('', home_view, name="home"),
    path('physics/', phy_view, name="physics"),
    path('chemistry/', chem_view, name="chemistry"),
    path('mathematics/', math_view, name="mathematics"),
    path('english/', eng_view, name="english"),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
