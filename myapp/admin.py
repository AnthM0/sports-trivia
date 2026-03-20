from django.contrib import admin
from .models import Player, TriviaCategory

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'stats')
    search_fields = ('name',)
    list_filter = ('sport',)

@admin.register(TriviaCategory)
class TriviaCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'sport', 'stat_code', 'verified', 'recommended_pinpoint', 'total_players')
    search_fields = ('title', 'stat_code')
    list_filter = ('sport', 'verified')