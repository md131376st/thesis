from django.conf.urls.static import static
from django.urls import path, include

from fileService import settings
from filemanger.views import Fileupload

# from rest_framework_simplejwt.views import TokenRefreshView
#
#
# from bookshelf.views import bookView
# from bookshelf.views.userView import MyObtainTokenPairView, RegisterView

app_name = 'filemanger'

urlpatterns = [
    path('upload', Fileupload.as_view()),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)