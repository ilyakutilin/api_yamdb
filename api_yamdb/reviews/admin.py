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
# TODO: ALEXEY
# Мы прошли целый спринт по Django, а сейчас мы уже делаем финальный проект
# по API. Мы научились разным и полезным вещам, поэтому стоит использовать
# одну очень полезную вещь, а именно регистрацию моделей в админке с помощью
# декоратора.
#
# from django.contrib import admin
#
#
# @admin.register(<имя модели>)
# class ... (admin.ModelAdmin)
#     ...
# https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#the-register-decorator
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(GenresTitles)
