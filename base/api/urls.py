from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('',  views.getRoutes),
    path('rooms/', views.getRooms),
    path('rooms/<str:pk>/', views.getRoom),
    path('users/', views.getUsers),
    path('users/<str:pk>/', views.getUser),
    path('topics/', views.getTopics),
    path('topics/<str:pk>/', views.getTopic),
    path('messages/', views.getMessages),

    path('room_messages/<str:pk>/', views.getRoomMessages),

    path('homeAPI/',views.homeAPI),
    path('roomAPI/<str:pk>/',views.roomAPI),

    # path('api/get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
    path('create-roomAPI/', views.createRoomAPI),

    path('user-profileAPI/<str:pk>/',views.userProfileAPI),

    path('room_create_message/<str:pk>/',views.createMessageAPI),

    path('register-userAPI/', views.register_user),

    path('delete-roomAPI/<str:pk>/', views.deleteRoomAPI),

    path('delete-messageAPI/<str:pk>/', views.deleteMessageAPI),

    path('update-roomAPI/<str:pk>/',views.updateRoomAPI),

    path('update-user-profileAPI/',views.updateUserProfileAPI),
]
