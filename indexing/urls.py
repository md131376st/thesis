from django.urls import path

from indexing.view.IndexCreationView import IndexCreationView
from indexing.view.IndexRetrivalView import IndexRetrivalView
from indexing.view.celeryMangerView import CeleryManger

app_name = 'indexing'
urlpatterns = [
    path('taskstate/<uuid:id>/', CeleryManger.as_view()),  # gives the state of the tasks #task/state/<uuid:id>/
    path('indexretrieval', IndexRetrivalView.as_view()),
    # data una domanda ritorna i documenti più rilevanti # document/retri
    path('indexcreation', IndexCreationView.as_view())  # crea un indice della code base
]