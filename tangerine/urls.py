from django.urls import path

from blog import views

app_name = 'blog'
urlpatterns = [
    path('<int:year>/<int:month>/<slug:slug>/', views.post_detail, name="post_detail"),
    path('cat/<str:cat_slug>/', views.category, name="category"),
]
