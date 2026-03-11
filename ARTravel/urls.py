"""
URL configuration for ARTravel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views as ar_views # Renumește views pentru claritate
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ar_views.index, name="home"),
    path('about/', ar_views.about, name="about"),
    path('attractions/', ar_views.attractions, name="attractions"),
    path('journey/', ar_views.journey, name="journey"),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/register/', ar_views.register, name='register'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('category/<str:category_name>/', ar_views.category_view, name='category_page'),
    path('favorite/toggle/<int:locatie_id>/', ar_views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', ar_views.favorite_list, name='favorite_list'),
    path('generate-route/', ar_views.generate_route, name='generate_route'),
    path('reviews/', ar_views.reviews, name='reviews'),
    path('instructions/', ar_views.instructions, name='instructions'),
    path('routes_list/', ar_views.routes_list, name='routes'),
    path('delete_route/<int:route_id>/', ar_views.delete_route, name='delete_route'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
