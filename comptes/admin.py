from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Compte


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):

    list_display = ("id", "libelle", "releve_compte")

    def releve_compte(self, obj):
        url = reverse("releve_compte", args=[obj.id])
        return format_html('<a href="{}">Relevé</a>', url)

    releve_compte.short_description = "Relevé"