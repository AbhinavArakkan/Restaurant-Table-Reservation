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
    path('userinput/', views.userinput, name='userinput'),
    path('get_upcoming_reservations/', views.get_upcoming_reservations, name='get_upcoming_reservations'),
    path('get_previous_reservations/', views.get_previous_reservations, name='get_previous_reservations'),
    path('reservation/get_reservations/', views.get_reservations, name='get_reservations'),
    path('reservation/send_reservation_email/', views.send_reservation_email, name='send_reservation_email'),
    path('add_food_item/', views.add_food_item, name='add_food_item'),
    path('fetch_food_items/', views.fetch_food_items, name='fetch_food_items'),
    path('delete_selected_food_items/', views.delete_selected_food_items, name='delete_selected_food_items'),
]