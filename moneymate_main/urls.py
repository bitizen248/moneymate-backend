from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from moneymate_main import views

urlpatterns = [
    url(r'^register/$', views.VkRegistration.as_view()),

    url(r'^vk/friends/$', views.vk_integration.getFriends),

    url(r'^roomsAndUsers/lastUpdates/$', views.rooms_and_users.lastUpdates),
    url(r'^roomsAndUsers/createRoom/$', views.rooms_and_users.createRoom),
    url(r'^roomsAndUsers/getRoomsAndUsers/$', views.rooms_and_users.getRoomsAndUsers),
    url(r'^roomsAndUsers/getMessage/$', views.rooms_and_users.getMessages),
    url(r'^roomsAndUsers/sendMessage/$', views.rooms_and_users.sendMessage),
    url(r'^roomsAndUsers/getUsers/$', views.rooms_and_users.getUsers),

    url(r'^check/getCheck/$', views.check.getCheck),
    url(r'^check/createCheck/$', views.check.createCheck),
    url(r'^check/deleteCheck/$', views.check.deleteCheck),

    url(r'^transations/feed/$', views.transactions.feed)
]

urlpatterns = format_suffix_patterns(urlpatterns)
