"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from Trade.views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingView.as_view(), name='landing'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('add/', TradeCreateView.as_view(), name='trade_create'),
    path('list/', TradeListView.as_view(), name='trade_list'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('trade/<int:pk>/edit/', TradeUpdateView.as_view(), name='edit_trade'),
    path('trade/<int:pk>/delete/', TradeDeleteView.as_view(), name='delete_trade'),
    path("register/", register_view, name="register"),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path("feedback/",FeedbackView.as_view(),name="feedback"),
    path("profile/",ProfileView.as_view(),name="profile"),
]
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'