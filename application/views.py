import os
from django.shortcuts import render
from celery.result import AsyncResult
from rest_framework import status
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from rest_framework.decorators import api_view
from .tasks import speech2face_task
from celery import uuid
from speech2face.settings import MEDIA_ROOT
from celery.states import PENDING, STARTED, RETRY, SUCCESS, REVOKED, FAILURE
from .models import UserTask
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def record_audio(request):
    return render(request, 'record.html')


@api_view(['POST'])
def submit_speech2face_task(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    audio_file = request.FILES.get('audio_file', None)
    if audio_file is None:
        return HttpResponseBadRequest()

    task_id = uuid()

    UserTask.objects.create(user=request.user, task_id=task_id)

    file_path = os.path.join(MEDIA_ROOT, f'{task_id}.wav')
    with open(file_path, 'wb+') as f:
        for chunk in audio_file.chunks():
            f.write(chunk)

    speech2face_task.apply_async((file_path,), task_id=task_id)

    return JsonResponse({'task_id': task_id}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def speech2face_task_list(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    user_tasks = UserTask.objects.filter(user__username=request.user.username).values_list('task_id', flat=True)
    response = []
    for task_id in user_tasks:
        task_result = AsyncResult(task_id)

        if task_result.status == SUCCESS:
            response.append({'task_id': task_id,
                             'status': task_result.status,
                             'result': task_result.result})
        else:
            response.append({'task_id': task_id,
                             'status': task_result.status})

    return JsonResponse(response, safe=False, status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE'])
def manage_speech2face_task(request, task_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    user_task = UserTask.objects.filter(user__username=request.user.username, task_id=task_id)
    if not user_task.exists():
        return HttpResponseNotFound()

    task_result = AsyncResult(task_id)

    if request.method == 'GET':

        if task_result.status in (PENDING, RETRY, STARTED):
            return JsonResponse({'status': task_result.status}, status=status.HTTP_202_ACCEPTED)

        elif task_result.status == SUCCESS:
            return JsonResponse({'status': task_result.status,
                                 'result': task_result.result}, status=status.HTTP_200_OK)

        elif task_result.status == REVOKED:
            return JsonResponse({'status': task_result.status}, status=status.HTTP_200_OK)

        else:
            return JsonResponse({'status': task_result.status}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        task_result.revoke(terminate=True)
        user_task.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)
