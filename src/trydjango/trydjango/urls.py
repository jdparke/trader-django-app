"""trydjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from pages import views
from users.views import user_detail_view
from calc_stat.views import download_view, ajax_calc_stat
from calc_plot.views import ajax_calc_plot
from portfolios.views import portfolio_view
from sectors.views import sector_view

urlpatterns = [
    path('', views.home_view),
    path('home/', views.home_view),
    path('contact/', views.contact_view),
    path('user/', user_detail_view),
    path('admin/', admin.site.urls),
    path('download/', download_view),
    path('portfolio/', portfolio_view),
    path('sector/', sector_view),
    path('post/ajax/calc_stat', ajax_calc_stat, name="post_calc_stat"),
    path('post/ajax/calc_plot', ajax_calc_plot, name="post_calc_plot")
]
