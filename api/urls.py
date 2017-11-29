from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^routes$', views.routes, name='routes'),
    url(r'^routes/(?P<route_id>\d+)/$', views.route_by_id, name='route-id'),
    url(r'^route-detail$', views.route_detail, name='route-detail'),
    url(r'^add-rating$', views.add_rating, name='add-rating'),
]
