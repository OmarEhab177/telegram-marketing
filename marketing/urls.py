from django.urls import path

from . import views

app_name = 'marketing'

urlpatterns = [
    path('', views.setup, name='setup'),
    path('verification/', views.verification, name='verification'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('get-channels/', views.get_channels, name='get-channels'),
    path('get-members', views.get_members, name='get-members'),
    path('create-channel', views.create_channel, name='create-channel'),
    path('logout', views.logout_view, name='logout'),
    path('invite-members', views.invite_members_to_channel, name='invite-members'),
    path('send-message/<str:channel_id>', views.send_message, name='send-message'),
    path('request-join', views.request_to_join_channel, name='request-join'),
]
