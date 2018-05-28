from django.contrib import admin

#from .models import PageView
from .models import CarouselImages, News, Locations, ProductsTypes, Products, Menus, ProductsSubtypes, GeneralSettings


# Register your models here.


class PageViewAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'timestamp']

#admin.site.register(PageView, PageViewAdmin)
admin.site.register(News)
admin.site.register(Locations)
admin.site.register(ProductsTypes)
admin.site.register(Products)
admin.site.register(Menus)
admin.site.register(ProductsSubtypes)
admin.site.register(GeneralSettings)
