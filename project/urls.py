from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

#from welcome.views import index, health
from welcome import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    path('', views.main_view, name='main'),
    path('carousel_async/', views.carousel_view, name='carousel'),
    path('news_async/', views.news_view, name='news'),
    path('about_async/', views.about_view, name='about'),
    path('contacts_async/', views.contacts_view, name='contacts'),
    path('contacts/', views.contacts_view_full, name='contacts_full'),
    # path('contacts_static/', views.contacts_static_view, name='contacts_static'),
    path('contacts/locations/', views.get_locations, name='locations'),
    path('delivery/', views.delivery_view_full, name='delivery_full'),
    path('delivery_async/', views.delivery_view, name='delivery'),
    path('vacancy/', views.vacancy_view_full, name='contacts'),
    path('vacancy_async/', views.vacancy_view, name='contacts'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('products_hot_async/', views.products_view_soups, name='soups'),
    path('products_hot/', views.products_view_soups_full, name='soups'),
    path('products_cold_async/', views.products_view_salads, name='salads'),
    path('products_cold/', views.products_view_salads_full, name='salads'),
    path('products_office_async/', views.products_view_office, name='salads'),
    path('products_office/', views.products_view_office_full, name='salads'),
    path('add_to_cart/', views.add_to_cart_view, name='add_to_cart'),
    path('cart_async/', views.cart_view, name='add_to_cart'),
    path('cart/', views.cart_view_full, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart_view, name='add_to_cart'),
    path('checkout_async/', views.checkout_view, name='checkout'),
    path('checkout/', views.checkout_view_full, name='checkout'),
    path('thankyou_async/', views.thankyou_view, name='thankyou'),
    path('thankyou/', views.thankyou_view_full, name='thankyou'),
    path('order/', views.order_view, name='order'),
    path('cookie_confirm/', views.cookie_confirm_view, name='order'),
    # path('cart_content/', views.remove_from_cart_view, name='add_to_cart'),
    path('admin/', admin.site.urls),

                  #url(r'^$', index),
    #url(r'^health$', health),
    #url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
