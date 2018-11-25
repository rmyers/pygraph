from django.contrib import admin

from .models import Site, Kind, Override


admin.site.register(Site)
admin.site.register(Kind)
admin.site.register(Override)
