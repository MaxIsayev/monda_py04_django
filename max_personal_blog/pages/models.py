from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


class Category(models.Model):
    name = models.CharField(_("name"), max_length=100, db_index=True)
    owner = models.ForeignKey(
        get_user_model(), 
        on_delete=models.CASCADE, 
        verbose_name=_("owner"), 
        related_name='categories',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ['name']

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"pk": self.pk})


class Page(models.Model):
    name = models.CharField(_("name"), max_length=100, db_index=True)
    description = models.TextField(_("description"), blank=True, max_length=10000)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE, 
        verbose_name=_("category"), 
        related_name='pages',
    )
    owner = models.ForeignKey(
        get_user_model(), 
        on_delete=models.CASCADE, 
        verbose_name=_("owner"), 
        related_name='pages',
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True, db_index=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ['name', '-created_at']

    def get_absolute_url(self):
        return reverse("page_detail", kwargs={"pk": self.pk})
