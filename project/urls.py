from django.contrib import admin
from django.urls import include, path
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', blog_views.home),
    # path('users/', include('users.urls')),
    path('blog/', include('blog.urls'))
]
