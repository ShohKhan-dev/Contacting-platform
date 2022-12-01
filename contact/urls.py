from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [    
    path('', views.home, name='home'),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path('conversation/<int:user_id>', views.conversation, name='conversation'),
    path('add_message', views.add_message, name='add_message'),
    path('notifications', views.notifications, name='notifications'),
    path('filter_users', views.filter_users, name='filter_users'),

    path('request_new_info', views.request_new_info, name='request_new_info'),
    path('search', views.search_results, name='search'),
    path('group_filter', views.group_filter, name='group_filter'),
    path('multisend_message', views.multisend_message, name='multisend_message'),
]