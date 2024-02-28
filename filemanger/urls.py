from django.conf.urls.static import static
from django.urls import path

from fileService import settings
from indexing.view.IndexCreationView import IndexCreationView
from indexing.view.IndexRetrivalView import IndexRetrivalView
from filemanger.view.ChromaDBView import CollectionInfo
from filemanger.view.EmbeddingView import EmbeddingView
from filemanger.view.fileMangerView import Fileupload, Pipline, PreProcess, FeatureExtract
from indexing.view.celeryMangerView import CeleryManger

app_name = 'filemanger'

urlpatterns = [
    path('upload', Fileupload.as_view()),  # caricare i file docx nel db
    path('process', PreProcess.as_view()),  # preprocessa i file
    path('feature_extractor', FeatureExtract.as_view()),  # da finire
    path('applypipeline', Pipline.as_view()),  # caricare e processare il file
    path('embedding', EmbeddingView.as_view()),
    # una lista di stringhe viene convertita in vettori e viene stored nel db # embedd/store
    path('collections', CollectionInfo.as_view()),  # da la lista di collections di chroma #collections/list
    path('taskstate/<uuid:id>/', CeleryManger.as_view()),  # gives the state of the tasks #task/state/<uuid:id>/
    path('indexretrieval', IndexRetrivalView.as_view()),
    # data una domanda ritorna i documenti più rilevanti # document/retri
    path('indexcreation', IndexCreationView.as_view())  # crea un indice della code base

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
