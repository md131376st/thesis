from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.response import Response

from fileService.celery import app
from filemanger.serializer.celerySerializer import CelerySerializer


class CeleryManger(RetrieveDestroyAPIView):
    serializer_class = CelerySerializer

    def get(self, request, *args, **kwargs):

        task_id = self.kwargs.get('id')
        if task_id is not None:
            task_id_str = str(task_id)  # Convert UUID to string
        else:
            return Response({'error': 'Task ID not provided'}, status=400)

        task_result = app.AsyncResult(task_id_str)
        response_data = {
            'task_id': task_id_str,
            'state': task_result.state,

        }

        return Response(response_data)


