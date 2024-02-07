from django.conf.urls.static import static
from django.urls import path, include

from fileService import settings
from filemanger.views import Fileupload, PreProcess, Pipline, FeatureExtract, EmbeddingView, CollectionInfo

app_name = 'filemanger'

urlpatterns = [
    path('upload', Fileupload.as_view()),
    path('process', PreProcess.as_view()),
    path('feature_extractor', FeatureExtract.as_view()),
    path('applypipline', Pipline.as_view()),
    path('embedding', EmbeddingView.as_view()),
    path('Collections', CollectionInfo.as_view())

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
