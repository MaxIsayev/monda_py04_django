from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from . import models, forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse
from django.db.models.query import QuerySet
from typing import Any
from datetime import datetime
# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    pages = models.Page.objects
    unpublished_pages = pages.filter(is_published=False)
    common_dashboard = [
        (_('users').title(), get_user_model().objects.count()),
        (
            _('categories').title(), 
            models.Category.objects.count(), 
            reverse('category_list'),
        ),
        (
            _('pages').title(), 
            pages.count(), 
            reverse('page_list'),
        ),
        (
            _('unpublished pages').title(), 
            unpublished_pages.count(),
        ),       
        (
            _('published pages').title(), 
            pages.filter(is_published=True).count(),
        ),
    ]
    if request.user.is_authenticated:
        user_pages = pages.filter(owner=request.user)
        user_unpublished_pages = user_pages.filter(is_published=False)
        user_dashboard = [
            (
                _('categories').title(), 
                models.Category.objects.filter(owner=request.user).count(), 
                reverse('category_list') + f"?owner={request.user.username}",
            ),
            (
                _('pages').title(), 
                user_pages.count(),
                reverse('page_list') + f"?owner={request.user.username}",
            ),
            (
                _('unpublished pages').title(), 
                user_unpublished_pages.count(),
            ),           
        ]
        unpublished_pages = user_unpublished_pages.all()[:5]
    else:
        user_dashboard = None
        unpublished_pages = unpublished_pages.all()[:5]

    context = {
        'common_dashboard': common_dashboard,
        'user_dashboard': user_dashboard,
        'unpublished_pages': unpublished_pages,
    }
    return render(request, 'pages/index.html', context)

def page_list(request: HttpRequest) -> HttpResponse:
    queryset = models.Page.objects
    owner_username = request.GET.get('owner')
    if owner_username:
        owner = get_object_or_404(get_user_model(), username=owner_username)
        queryset = queryset.filter(owner=owner)
        categories = models.Category.objects.filter(owner=owner)
    else:
        categories = models.Category.objects.all()
    category_pk = request.GET.get('category')
    if category_pk:
        category = get_object_or_404(models.Category, pk=category_pk)
        queryset = queryset.filter(category=category) 
    search_name = request.GET.get('search_name')
    if search_name:
        queryset = queryset.filter(name__icontains=search_name)
    context = {
        'page_list': queryset.all(),
        'category_list': categories.all(),
        'user_list': get_user_model().objects.all().order_by('username'),
        'next': reverse('page_list') + '?' + '&'.join([f"{key}={value}" for key, value in request.GET.items()]),
    }
    return render(request, 'pages/page_list.html', context)

def page_detail(request: HttpRequest, pk:int) -> HttpResponse:
    return render(request, 'pages/page_detail.html', {
        'page': get_object_or_404(models.Page, pk=pk)
    })

def page_published(request: HttpRequest, pk:int) -> HttpResponse:
    page = get_object_or_404(models.Page, pk=pk)
    if request.user in [page.owner, page.category.owner]:
        page.is_published = not page.is_published
        page.save()    
        messages.info(request, "{} {} {} {}".format(
            _('page').capitalize(),
            page.name,
            _('marked as'),
            _('published') if page.is_published else _('not published'),
        ))
    else:
        messages.error(request, "{}: {}".format(
            _("permission error").title(),
            _("you must be the owner of either the page itself or it\'s category"),
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
    fields = ('name', 'description', )

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
    fields = ('name', 'description', )

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

@login_required
def page_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = forms.PageForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            messages.success(request, _("page created successfully").capitalize())
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return redirect('page_list')
    else:
        form = forms.PageForm()  
    form.fields['category'].queryset = form.fields['category'].queryset.filter(owner=request.user)
    return render(request, 'pages/page_create.html', {'form': form})

@login_required
def page_update(request: HttpRequest, pk: int) -> HttpResponse:
    page = get_object_or_404(models.Page, pk=pk, owner=request.user)
    if request.method == "POST":
        form = forms.PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, _("page edited successfully"))
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return redirect('page_list')
    else:
        form = forms.PageForm(instance=page)
    form.fields['category'].queryset = form.fields['category'].queryset.filter(owner=request.user)
    return render(request, 'pages/page_update.html', {'form': form})

@login_required
def page_delete(request: HttpRequest, pk: int) -> HttpResponse:
    page = get_object_or_404(models.Page, pk=pk, owner=request.user)
    if request.method == "POST":
        page.delete()
        messages.success(request, _("page deleted successfully"))
        if request.GET.get('next'):
            return redirect(request.GET.get('next'))
        return redirect('page_list')
    return render(request, 'pages/page_delete.html', {'page': page, 'object': page})