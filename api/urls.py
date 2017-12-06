from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^media$', views.media, name='media'),
    url(r'^routes$', views.routes, name='routes'),
    url(r'^routes/(?P<route_id>\d+)/$', views.route_by_id, name='route-id'),
    url(r'^route-detail$', views.route_detail, name='route-detail'),
    url(r'^add-rating$', views.add_rating, name='add-rating'),
    url(r'^add-story$', views.add_story, name='add-story'),
    url(r'^add-poi$', views.add_poi, name='add-poi'),
    url(r'^check-sponsoring$', views.check_sponsoring, name='check-sponsoring'),
]
