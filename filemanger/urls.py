from django.urls import path, include

from filemanger.views import Fileupload

# from rest_framework_simplejwt.views import TokenRefreshView
#
#
# from bookshelf.views import bookView
# from bookshelf.views.userView import MyObtainTokenPairView, RegisterView

app_name = 'filemanger'

urlpatterns = [
    path('test', Fileupload.as_view()),

]
