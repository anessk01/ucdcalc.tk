from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from addition import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    url('home/$', views.home, name="addRow"),
    url('scrapeUCD/$', views.scrapeUCD, name="webScraping"),
    url(r'^', include('favicon.urls')),
]


