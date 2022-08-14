from django.contrib import admin

from .models import Category, Comment, Genre, GenresTitles, Review, Title


class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('author',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('author',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(GenresTitles)
