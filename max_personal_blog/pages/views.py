from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse
from django.db.models.query import QuerySet
from typing import Any

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

class CategoryListView(generic.ListView):
    model = models.Category
    template_name = 'pages/category_list.html'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        if self.request.GET.get('owner'):
            queryset = queryset.filter(owner__username=self.request.GET.get('owner'))
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['user_list'] = get_user_model().objects.all().order_by('username')
        return context


class CategoryDetailView(generic.DetailView):
    model = models.Category
    template_name = 'pages/category_detail.html'

class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Category
    template_name = 'pages/category_create.html'
    fields = ('name', )

    def get_success_url(self) -> str:
        messages.success(self.request, _('category created successfully').capitalize())
        return reverse('category_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
class CategoryUpdateView(
        LoginRequiredMixin, 
        UserPassesTestMixin, 
        generic.UpdateView
    ):
    model = models.Category
    template_name = 'pages/category_update.html'
    fields = ('name', )

    def get_success_url(self) -> str:
        messages.success(self.request, _('category updated successfully').capitalize())
        return reverse('category_list')

    def test_func(self) -> bool | None:
        return self.get_object().owner == self.request.user or self.request.user.is_superuser
    
class CategoryDeleteView(
        LoginRequiredMixin, 
        UserPassesTestMixin, 
        generic.DeleteView
    ):
    model = models.Category
    template_name = 'pages/category_delete.html'

    def get_success_url(self) -> str:
        messages.success(self.request, _('category deleted successfully').capitalize())
        return reverse('category_list')

    def test_func(self) -> bool | None:
        return self.get_object().owner == self.request.user or self.request.user.is_superuser

    