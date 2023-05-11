from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin (admin.ModelAdmin):
    list_display = [
        field.name for field in Post._meta.get_fields()
        if field.name != 'id'
    ]
    list_editable = (
        'is_published',
        'pub_date',
        'author'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


@admin.register(Category)
class CategoryAdmin (admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
        'slug'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin (admin.ModelAdmin):
    list_display = ('name', 'is_published')
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)
