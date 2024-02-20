from django.conf.urls.static import static
from django.urls import path, include

from fileService import settings
from filemanger.view.IndexCreationView import IndexCreationView
from filemanger.view.IndexRetrivalView import IndexRetrivalView
from filemanger.view.ChromaDBView import CollectionInfo
from filemanger.view.EmbeddingView import EmbeddingView
from filemanger.view.fileMangerView import Fileupload, Pipline, PreProcess, FeatureExtract
from filemanger.view.celeryMangerView import CeleryManger

app_name = 'filemanger'

urlpatterns = [
    path('upload', Fileupload.as_view()),
    path('process', PreProcess.as_view()),
    path('feature_extractor', FeatureExtract.as_view()),
    path('applypipline', Pipline.as_view()),
    path('embedding', EmbeddingView.as_view()),
    path('Collections', CollectionInfo.as_view()),
    path('taskstate/<uuid:id>/', CeleryManger.as_view()),
    path('indexretrival', IndexRetrivalView.as_view()),
    path('indexcration', IndexCreationView.as_view())

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
