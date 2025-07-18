from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import QuestionType, FAQ

@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 80})},
    }

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'type')
    list_filter = ('type',)
    search_fields = ('question', 'answer')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 80})},
    }