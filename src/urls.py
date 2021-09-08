from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf.urls import url
from addition import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.sitemaps.views import sitemap
from addition.sitemaps import Our_Sitemap

sitemaps = {
 'Our_sitemap' : Our_Sitemap(),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    url('home/$', views.home, name="addRow"),
    url('scrapeUCD/$', views.scrapeUCD, name="webScraping"),
    url('sitemap\.xml$', sitemap, {'sitemaps' : sitemaps}, name = 'django.contrib.sitemaps.views.sitemap'),
    path("favicon.ico/", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico"))),
    path("robots.txt/", lambda r: HttpResponse("User-agent: * \nDisallow: /admin/ \n\n\nSitemap: https://www.ucdcalc.tk/sitemap.xml", content_type="text/plain")),
    path("freedom.jpg/", RedirectView.as_view(url=staticfiles_storage.url("palestineflag.jpg"))),
    path("ears.jpeg/", RedirectView.as_view(url=staticfiles_storage.url("ears.jpeg"))),
    path("shoes.jpg/", RedirectView.as_view(url=staticfiles_storage.url("shoes.png"))),
    path("glory.jpg/", RedirectView.as_view(url=staticfiles_storage.url("SOOKA.png"))),
]

urlpatterns += staticfiles_urlpatterns()