from django.shortcuts import render
from django.http import HttpResponse

def acceuil(request):
    return render(request, "acceuil.html")