from django.urls import path

from tangerine import views

app_name = 'tangerine'
urlpatterns = [
    path('<int:year>/<int:month>/<slug:slug>/', views.post_detail, name="post_detail"),
    path('cat/<str:cat_slug>/', views.category, name="category"),
    path('', views.home, name="home"),
]
