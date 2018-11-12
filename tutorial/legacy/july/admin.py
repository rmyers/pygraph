from django.contrib import admin
from models import Game, Commit


admin.site.register(Commit, admin.ModelAdmin)
admin.site.register(Game, admin.ModelAdmin)
