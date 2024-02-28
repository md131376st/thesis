from django.urls import path

from indexing.view.IndexCreationView import IndexCreationView
from indexing.view.IndexRetrivalView import IndexRetrivalView
from indexing.view.celeryMangerView import CeleryManger

app_name = 'indexing'
urlpatterns = [
    path('task/state/<uuid:id>/', CeleryManger.as_view()),  # gives the state of the tasks #task/state/<uuid:id>/
    path('index/retrieve', IndexRetrivalView.as_view()),
    # data una domanda ritorna i documenti più rilevanti # document/retri
    path('index/store', IndexCreationView.as_view())  # crea un indice della code base
]