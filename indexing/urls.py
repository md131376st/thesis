from django.urls import path, register_converter

from indexing.types import TypeConverter
from indexing.view.DescriptionView import DescriptionViewSet
from indexing.view.IndexRetrivalView import IndexRetrivalView
from indexing.view.StoreEmbeddingsView import StoreEmbeddingsView
from indexing.view.CeleryMangerView import CeleryManger

app_name = 'indexing'

register_converter(TypeConverter, 'tc')

urlpatterns = [
    path('task/state/<uuid:id>/', CeleryManger.as_view()),  # gives the state of the tasks #task/state/<uuid:id>/
    path('index/retrieve', IndexRetrivalView.as_view()),
    path('description/<tc:type>',
         DescriptionViewSet.as_view(
             {'get': 'list',
              'post': 'create',
              'put': 'update',
              'delete': 'destroy'
              }
         )),

    # data una domanda ritorna i documenti più rilevanti # document/retri
    path('index', StoreEmbeddingsView.as_view())  # crea un indice della code base
]
