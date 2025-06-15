"""
URL configuration for webapp project.

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
from django.urls import path
from litrevu import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('flux/', views.flux, name='flux'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),
    path('create-review/', views.create_review, name='create_review'),
    path('posts/', views.posts, name='posts'),
    path('update-ticket/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
    path('delete-ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('update-review/<int:review_id>/', views.update_review, name='update_review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('unfollow-user/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('create-review/<int:ticket_id>/', views.create_review, name='create_review_for_ticket'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
