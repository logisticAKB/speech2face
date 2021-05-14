import os
from django.shortcuts import render
from celery.result import AsyncResult
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from .tasks import speech2face_task
from celery import uuid
from speech2face.settings import MEDIA_ROOT
from celery.states import PENDING, STARTED, RETRY, SUCCESS, REVOKED, FAILURE


def index(request):
    return render(request, 'index.html')


@api_view(['POST'])
def submit_speech2face_task(request):
    audio_file = request.FILES.get('audio_file', None)
    if audio_file is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    task_id = uuid()
    file_path = os.path.join(MEDIA_ROOT, f'{task_id}.wav')
    with open(file_path, 'wb+') as f:
        for chunk in audio_file.chunks():
            f.write(chunk)

    speech2face_task.apply_async((file_path, ), task_id=task_id)

    response = JSONRenderer().render({'task_id': task_id})
    return Response(response, content_type='application/json', status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'DELETE'])
def manage_speech2face_task(request, task_id):
    task_result = AsyncResult(task_id)

    if request.method == 'GET':

        if task_result.status in (PENDING, RETRY, STARTED):
            return Response(JSONRenderer().render({'status': task_result.status}),
                            content_type='application/json',
                            status=status.HTTP_202_ACCEPTED)

        elif task_result.status == SUCCESS:
            return Response(JSONRenderer().render({'status': task_result.status,
                                                   'result': task_result.result}),
                            content_type='application/json',
                            status=status.HTTP_200_OK)

        elif task_result.status == REVOKED:
            return Response(JSONRenderer().render({'status': task_result.status}),
                            content_type='application/json',
                            status=status.HTTP_200_OK)

        elif task_result.status == FAILURE:
            return Response(JSONRenderer().render({'status': task_result.status}),
                            content_type='application/json',
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':

        task_result.revoke(terminate=True)
        return Response(status=status.HTTP_202_ACCEPTED)
