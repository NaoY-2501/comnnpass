from django.conf.urls import include,url
from . import views
urlpatterns=[
    url(r'^$',views.top,name='top'),
    url(r'^search$',views.search,name='search'),
]
