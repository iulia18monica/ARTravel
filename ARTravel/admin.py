from django.contrib import admin
from .models import Locatie, Favorit,Review

# Această linie face ca "Locatie" să apară în panoul de admin
admin.site.register(Locatie)
admin.site.register(Favorit)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at') # Ce vezi în listă
    list_filter = ('rating', 'created_at') # Filtre în dreapta
    search_fields = ('content', 'user__username') # Posibilitate de căutare