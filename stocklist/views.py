from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello, world!")


def login_view(request):
    return HttpResponse("Hello, login!")

def register_view(request):
    return HttpResponse("Hello, register!")