from django.urls import path
from rango import views
from registration.backends.simple.views import RegistrationView

app_name = 'rango'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('category/<slug:category_name_slug>',
         views.show_category, name='show_category'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<slug:category_name_slug>/add_page',
         views.add_page, name='add_page'),
    path('search/', views.search, name='search'),
    path('suggest/', views.suggest_category, name='suggest_category'),
    path('goto/', views.track_url, name='goto'),
    path('like/', views.like_category, name='like_category'),

    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<username>', views.profile, name='profile'),
    path('register/', RegistrationView.as_view(
        success_url='/rango/register_profile/'), name='register'),

    path('profiles/', views.list_profiles, name='list_profiles'),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
