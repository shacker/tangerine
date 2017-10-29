from django.contrib import admin
from django.urls import include, path
from blog import views as blogviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', blogviews.home),
    # path('users/', include('users.urls')),
    path('blog/', include('blog.urls'))
]
