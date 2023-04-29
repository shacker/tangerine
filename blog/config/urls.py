from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

# from blog.tangerine.views import home, send_user_mail
from blog.tangerine.views import home
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", home, name="home"),
    # path("send_email", send_user_mail, name="send_user_mail"),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
