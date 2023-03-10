"""primafila URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from calendarik import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.homepage, name="homepage"),
#    path("add_event", views.add_event, name="add_event"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("search", views.search, name="search"),
    path("get_roles", views.get_roles, name="get_roles"),
    path("get_contact", views.get_contacts, name="get_contact"),
#    path("event", views.event, name="event"),
    path("edit_event", views.edit_event, name="edit_event"),
    path("contact", views.contact, name="contact"),
    path("contact_list", views.contact_list, name="contact_list"),
    path("travel", views.travel, name="travel"),
    path("other", views.other_event, name="other"),
    path("engagement", views.engagement, name="engagement"),
    path("contact/<int:contact_id>", views.edit_contact, name="edit_contact"),
]
