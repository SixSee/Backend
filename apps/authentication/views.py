from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

def ping(request):
    return HttpResponse("pong")