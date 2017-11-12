from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^routes$', views.routes, name='routes')
]
