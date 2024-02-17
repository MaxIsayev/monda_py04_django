from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    context = {
        'categories_count': models.Category.objects.count(),
        'pages_count': models.Page.objects.count(),
        'users_count': models.get_user_model().objects.count(),
    }
    return render(request, 'pages/index.html', context)

def page_list(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/page_list.html', {
        'page_list': models.Page.objects.all()
    })

def page_detail(request: HttpRequest, pk:int) -> HttpResponse:
    return render(request, 'pages/page_detail.html', {
        'page': get_object_or_404(models.Page, pk=pk)
    })

def page_published(request: HttpRequest, pk:int) -> HttpResponse:
    page = get_object_or_404(models.Page, pk=pk)
    page.is_published = not page.is_published
    page.save()    
    messages.info(request, "{} {} {} {}".format(
        _('page').capitalize(),
        page.name,
        _('marked as'),
        _('published') if page.is_published else _('not published'),
    ))
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return redirect(page_list)

dashboard = _('dashboard')