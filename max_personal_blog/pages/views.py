from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from . import models
# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    context = {
        'categories_count': models.Category.objects.count(),
        'pages_count': models.Page.objects.count(),
        'users_count': models.get_user_model().objects.count(),
    }
    return render(request, 'pages/index.html', context)