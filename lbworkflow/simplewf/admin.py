from django.contrib import admin

from .models import SimpleWorkFlow


class SimpleWorkFlowAdmin(admin.ModelAdmin):
    list_display = ('summary', 'content')


admin.site.register(SimpleWorkFlow, SimpleWorkFlowAdmin)
