"""
The application views defined here
"""
from django.shortcuts import get_object_or_404, render


def home(request):
    return render(request, 'index.html')
