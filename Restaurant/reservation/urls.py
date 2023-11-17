from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user,name='register'),
    path('', views.home, name='home'),
    path('Queens_Feast/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('reservations/', views.reservation, name='reservation'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('profile/change_photo/', views.change_profile_photo, name='change_profile_photo'),
    path('profile/upload_photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path('userinput/', views.userinput, name='userinput'),
]