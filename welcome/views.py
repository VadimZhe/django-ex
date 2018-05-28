import os
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail, BadHeaderError
from django.utils.formats import date_format
from django.template import loader

import datetime

from . import database
from .models import PageView, CarouselImages, News, Locations, ProductsTypes, Menus, Products, ShoppingCarts, ProductsInCart, ProductsSubtypes, GeneralSettings
from .forms import FeedbackForm

# Create your views here.

def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')
    PageView.objects.create(hostname=hostname)

    return render(request, 'welcome/index.html', {
        'hostname': hostname,
        'database': database.info(),
        'count': PageView.objects.count()
    })

def health(request):
    return HttpResponse(PageView.objects.count())

################################################################

def get_general_settings():
    our_settings = GeneralSettings.objects.get(pk=1)
    min_order_amount = our_settings.min_order_amount
    max_order_hour = our_settings.max_order_hour
    #retvalue
    return {'min_order_amount': min_order_amount, 'max_order_hour': max_order_hour}

class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

def main_view(request):
    return universal_view(request,
                          show_carousel=True,
                          show_news=True,
                          show_about=True)

def get_current_news_slice():
    return News.objects.exclude(date_actual__gt=datetime.datetime.now()).exclude(date_expire__lt=datetime.datetime.now())

def universal_view(request,
                   show_carousel=False,
                   show_news=False,
                   show_about=False,
                   show_contacts=False,
                   show_vacancy=False,
                   show_delivery=False,
                   show_products_hot=False,
                   show_cart=False,
                   show_salads=False,
                   show_checkout=False,
                   show_office=False,
                   show_thankyou=False):
    '''Render any set of the divs in accordance to the arguments

    navbar and footers are ALWAYS included'''

    render_parameters = dict()
    #print('cookie_warning_confirmed=', request.session['cookie_warning_confirmed'])
    #print('all cookies keys:', list(request.session.keys()))
    #print('show=','cookie_warning_confirmed' not in list(request.session.keys()))
    render_parameters['show_cookie_warning'] = 'cookie_warning_confirmed' not in list(request.session.keys())
    # Carousel (now parallax)
    render_parameters['show_carousel'] = show_carousel
    #if show_carousel:
    #    carousel_images = CarouselImages.objects.all()
    #    render_parameters['carousel_images'] = carousel_images
    render_parameters['show_news'] = show_news
    if show_news:
        add_news_parameters(render_parameters)
        #current_news_slice = get_current_news_slice()
        #print(datetime.date.today())
        #render_parameters['current_news'] = current_news_slice
    render_parameters['show_about'] = show_about
    render_parameters['show_contacts'] = show_contacts
    if show_contacts:
        add_contacts_form_parameter(render_parameters)
        #render_parameters['form'] = FeedbackForm
    #our_locations = Locations.objects.all()
    render_parameters['locations'] = Locations.objects.all() #our_locations
    #menu_sections = ProductsTypes.objects.all()
    render_parameters['menu_sections'] = ProductsTypes.objects.all() #menu_sections
    cart = ShoppingCarts(request)
    render_parameters['cart_total_amount'] = cart.get_total_amount()
    render_parameters['show_vacancy'] = show_vacancy
    render_parameters['show_delivery'] = show_delivery
    render_parameters['show_products_hot'] = show_products_hot
    if show_products_hot:
        add_soups_parameters(render_parameters)
        #current_type = ProductsTypes.objects.get(pk=1)
        #title_image = current_type.picture
        #if title_image:
        #    title_image_path = title_image.url
        #else:
        #    title_image_path = ''
        #days_list = Menus.objects.filter(day__gt=datetime.date.today()).prefetch_related('offered').all()
        #render_parameters['product_type'] = current_type
        #render_parameters['days_list'] = days_list
        #render_parameters['title_image_path'] = title_image_path
    render_parameters['show_cart'] = show_cart
    if show_cart:
        add_cart_parameters(request, render_parameters)
        #cart = ShoppingCarts(request)
        #tmp_arr = cart.get_products_in_cart()
        #render_parameters['products_in_cart'] = tmp_arr
        #if cart.date is None:
        #    cart_date_str = ''
        #else:
        #    cart_date_str = date_format(cart.date, 'd.m')
        #render_parameters['cart_date'] = cart_date_str
        #render_parameters['totals'] = cart.get_totals()
        #render_parameters['too_late'] = cart.expired()
        #render_parameters['min_order_amount'] = get_general_settings()['min_order_amount']
        #render_parameters['max_order_hour'] = get_general_settings()['max_order_hour']
        #print('cart_date=', cart.date, 'today=', datetime.date.today())
    render_parameters['show_salads'] = show_salads
    if show_salads:
        add_salads_parameters(render_parameters)
        #current_type = ProductsTypes.objects.get(pk=2) #TODO: think of something better than PK
        #title_image = current_type.picture
        #if title_image:
        #    title_image_path = title_image.url
        #else:
        #    title_image_path = ''
        #subtypes_list = ProductsSubtypes.objects.filter(type=current_type).all() #prefetch_related('offered').all()
        #render_parameters['product_type'] = current_type
        #render_parameters['subtypes'] = subtypes_list
        #render_parameters['products'] = Products.objects.filter(type=current_type).all()
        #render_parameters['title_image_path'] = title_image_path
    render_parameters['show_office'] = show_office
    if show_office:
        add_office_parameters(render_parameters)
        #current_type = ProductsTypes.objects.get(pk=3) #TODO: think of something better than PK
        #title_image = current_type.picture
        #if title_image:
        #    title_image_path = title_image.url
        #else:
        #    title_image_path = ''
        #subtypes_list = ProductsSubtypes.objects.filter(type=current_type).all() #prefetch_related('offered').all()
        #render_parameters['product_type'] = current_type
        #render_parameters['products'] = Products.objects.filter(type=current_type).all()
        #render_parameters['title_image_path'] = title_image_path

    render_parameters['show_checkout'] = show_checkout
    if show_checkout:
        add_checkout_parameters(request, render_parameters)
        #cart = ShoppingCarts(request)
        #render_parameters['products_in_cart'] = cart.get_products_in_cart()
        #render_parameters['cart_date'] = cart.date
        #render_parameters['totals'] = cart.get_totals()
        #render_parameters['default_delivery_time'] = cart.get_default_delivery_time()
    render_parameters['show_thankyou'] = show_thankyou

    return render(request, 'main.html', render_parameters)

def checkout_view(request):
    render_parameters = dict()
    add_checkout_parameters(request, render_parameters)
    return render(request, 'checkout.html', render_parameters)

def add_checkout_parameters(request, render_parameters):
    if 'locations' not in render_parameters:
        render_parameters['locations'] = Locations.objects.all()
    cart = ShoppingCarts(request)
    render_parameters['products_in_cart'] = cart.get_products_in_cart()
    render_parameters['cart_date'] = cart.date
    render_parameters['totals'] = cart.get_totals()
    render_parameters['default_delivery_time'] = cart.get_default_delivery_time()

def thankyou_view(request):
    return render(request, 'thankyou.html', {})

def thankyou_view_full(request):
    return universal_view(request, show_thankyou=True)

def cart_view(request):
    '''Render shopping cart div'''
    render_parameters = dict()
    add_cart_parameters(request, render_parameters)
    #cart = ShoppingCarts(request)
    #tmp_arr = cart.get_products_in_cart()
    #render_parameters['products_in_cart'] = tmp_arr
    #if cart.date is None:
    #    render_parameters['cart_date'] = ''#None
    #else:
    #    render_parameters['cart_date'] =  date_format(cart.date,'d.m')
    #render_parameters['too_late'] = cart.expired()#.date() < datetime.date.today()
    #render_parameters['totals'] = cart.get_totals()
    #render_parameters['min_order_amount'] = get_general_settings()['min_order_amount']
    return render(request, 'cart.html', render_parameters)#{'products_in_cart': cart.get_products_in_cart(),
                                         #'cart_total_amount': cart.get_total_amount(),
                                         #'totals': cart.get_totals()})

def add_cart_parameters(request, render_parameters):
    cart = ShoppingCarts(request)
    render_parameters['products_in_cart'] = cart.get_products_in_cart()
    if cart.date is None:
        render_parameters['cart_date'] = ''#None
    else:
        render_parameters['cart_date'] =  date_format(cart.date,'d.m')
    render_parameters['too_late'] = cart.expired()
    render_parameters['totals'] = cart.get_totals()
    render_parameters['min_order_amount'] = get_general_settings()['min_order_amount']

def products_view_soups(request):
    render_parameters = dict()
    add_soups_parameters(render_parameters)
    #current_type = ProductsTypes.objects.get(pk=1)
    #title_image = current_type.picture
    #if title_image:
    #    title_image_path = title_image.url
    #else:
    #    title_image_path = ''
    #days_list = Menus.objects.filter(day__gt=datetime.date.today()).prefetch_related('offered').all()
    #even_count = len(days_list) % 2 == 0
    return render(request, 'soup_and_hot.html', render_parameters)
        #'product_type': current_type,
        #'days_list': days_list,
        #'even_count': even_count,
        #'title_image_path': title_image_path,
    #})

def add_soups_parameters(render_parameters):
    current_type = ProductsTypes.objects.get(pk=1)
    render_parameters['product_type'] = current_type
    #title_image = current_type.picture
    #if title_image:
    #    title_image_path = title_image.url
    #else:
    #    title_image_path = ''
    render_parameters['title_image_path'] = get_product_image_path(current_type)
    days_list = Menus.objects.filter(day__gt=datetime.date.today()).prefetch_related('offered').all()
    render_parameters['days_list'] = days_list
    render_parameters['even_count'] = len(days_list) % 2 == 0

def products_view_salads(request):
    render_parameters = dict()
    add_salads_parameters(render_parameters)
    #current_type = ProductsTypes.objects.get(pk=2)
    #title_image = current_type.picture
    #if title_image:
    #    title_image_path = title_image.url
    #else:
    #    title_image_path = ''
    #subtypes_list = ProductsSubtypes.objects.filter(type=current_type).all()  # prefetch_related('offered').all()
    return render(request, 'salads.html', render_parameters)
        #'product_type': current_type,
        #'subtypes': subtypes_list,
        #'products': Products.objects.filter(type=current_type).all(),
        #'title_image_path': title_image_path,
    #})

def add_salads_parameters(render_parameters):
    current_type = ProductsTypes.objects.get(pk=2)
    render_parameters['product_type'] = current_type
    render_parameters['title_image_path'] = get_product_image_path(current_type)
    render_parameters['subtypes'] = ProductsSubtypes.objects.filter(type=current_type).all()  # prefetch_related('offered').all()
    render_parameters['products'] = Products.objects.filter(type=current_type).all()
    render_parameters['title_image_path'] = get_product_image_path(current_type)

def get_product_image_path(product_type):
    image = product_type.picture
    if image:
        return image.url
    else:
        return ''

def products_view_office(request):
    render_parameters = dict()
    add_office_parameters(render_parameters)
    #current_type = ProductsTypes.objects.get(pk=3)
    #title_image = current_type.picture
    #if title_image:
    #    title_image_path = title_image.url
    #else:
    #    title_image_path = ''
    return render(request, 'office.html', render_parameters)
        #'product_type': current_type,
        #'products': Products.objects.filter(type=current_type).all(),
        #'title_image_path': title_image_path,
    #})

def add_office_parameters(render_parameters):
    current_type = ProductsTypes.objects.get(pk=3)
    render_parameters['product_type'] = current_type
    render_parameters['products'] = Products.objects.filter(type=current_type).all()
    render_parameters['title_image_path'] = get_product_image_path(current_type)

def products_view_soups_full(request):
    return universal_view(request, show_products_hot=True)

def contacts_view(request):
    render_parameters = dict()
    render_parameters['locations'] =Locations.objects.all()
    add_contacts_form_parameter(render_parameters)
    #menu_sections = ProductsTypes.objects.all()
    #fb_form = FeedbackForm()
    #cart = ShoppingCarts(request)
    return render(request, 'contacts.html', render_parameters)

def contacts_view_full(request):
    return universal_view(request,
                          show_contacts=True)

def add_contacts_form_parameter(render_parameters):
    render_parameters['form'] = FeedbackForm()

def carousel_view(request):
    return render(request, 'carousel.html', {}) #'carousel_images': CarouselImages.objects.all()})

def news_view(request):
    render_parameters = dict()
    add_news_parameters(render_parameters)
    return render(request, 'news.html', render_parameters)

def add_news_parameters(render_parameters):
    render_parameters['current_news'] = get_current_news_slice()

def about_view(request):
    return render(request, 'about.html', {})

def get_locations(request):
    our_locations = Locations.objects.all().values()
    #menu_sections = ProductsTypes.objects.all()
    return JsonResponse({'locations': list(our_locations)})

def delivery_view(request):
    return render(request, 'delivery.html', {})

def delivery_view_full(request):
    return universal_view(request, show_delivery=True)

def vacancy_view(request):
    return render(request, 'vacancy.html', {})

def vacancy_view_full(request):
    return universal_view(request, show_vacancy=True)

def products_view_salads_full(request):
    return universal_view(request, show_salads=True)

def products_view_office_full(request):
    return universal_view(request, show_office=True)

def order_view(request):
    result = 0
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = CheckoutForm(request.POST)
        # check whether it's valid:
        if True:#form.is_valid():
            # process the data in form.cleaned_data as required
            subject = 'Заказ с сайта Fresh Point'
            message = 'Клиент: {}, тел.{}'.format(
                request.POST.get('client_name', ''),
                request.POST.get('phone', ''))
            message += chr(13)
            #print('address_visible is', request.POST.get('address_visible'))
            if request.POST.get('address_visible') == 'true':
                message += 'Заказал доставку на адрес {} {}'.format(
                    request.POST.get('address'),
                    request.POST.get('address2'))
                delivery_address = 'На адрес: ' + request.POST.get('address') + ' ' + request.POST.get('address2')
            else:
                message += 'Заберёт сам из кафе: ' + request.POST.get('cafe_to_pick_up')
                delivery_address = 'Самовывоз из кафе ' + request.POST.get('cafe_to_pick_up')
            #print('delivery_address is', delivery_address)
            message += chr(13)
            delivery_time_str = request.POST.get('delivery_time')
            #print(delivery_time_str)
            #print('type = ', type(delivery_time_str))
            message += 'Время доставки: {}'.format(
                request.POST.get('delivery_time'))
            message += chr(13)
            message += 'Приборы: {}'.format(
                request.POST.get('flatware'))
            message += chr(13)
            if request.POST.get('hot_delivery') == 'true':
                hot_delivery_str = 'Да'
            else:
                hot_delivery_str = 'Нет'
            message += 'Доставка в горячем виде: {}'.format(
                request.POST.get('hot_delivery'))
            message += chr(13)
            if request.POST.get('payment_method') == 'id_payment_cash':
                payment_str = 'Оплата наличными'
            else:
                payment_str = 'Оплата безналичная'
            message += payment_str
            message += chr(13)
            message += 'Состав заказа:'+chr(13)
            cart = ShoppingCarts(request)
            products_in_cart = cart.get_products_in_cart()
            for item in products_in_cart:
                message += item['product_name'] + ':' + chr(9) + chr(9) + chr(9) \
                           + str(item['product_price']) + ' руб. * ' \
                           + str(item['amount']) + ' шт. = ' \
                           + str(item['cost']) + 'руб.' + chr(13)
            cart_totals = cart.get_totals()
            message += 'Итого позиций: ' + str(cart_totals['total_amount']) + ' на общую сумму ' + str(cart_totals['total_cost']) + ' руб.'
            client_email = request.POST.get('sender', '')
            html_message = loader.render_to_string(
                'email.html',
                {
                    'client_name': request.POST.get('client_name', ''),
                    'phone': request.POST.get('phone', ''),
                    'delivery': delivery_address,
                    'delivery_time': request.POST.get('delivery_time', ''),
                    'flatware': request.POST.get('flatware', ''),
                    'hot_delivery': hot_delivery_str, # request.POST.get('hot_delivery', ''),
                    'payment_method': payment_str,
                    'products_in_cart': products_in_cart,
                    'totals': cart_totals
                }
            )
            if subject and message and client_email:
                try:
                    None
                    result = send_mail(subject, message, 'info@fresh-point.com', [client_email, 'vadim.zherdev@gmail.com'], html_message=html_message)
                except BadHeaderError:
                    return JsonResponse({'result': result, 'message': 'Invalid header found.'})
                return JsonResponse({'result': result, 'message': 'Ваше сообщение отправлено, спасибо!'})
            else:
                return JsonResponse(
                    {'result': result, 'message': 'empty fields: "' + subject + '", "' + message + '", "' + from_email})
        else:
            print(form.errors)
            return JsonResponse({'result': result, 'message': form.errors})
    else:
        form = FeedbackForm()
    return JsonResponse({'result': result, 'message': 'request method is not POST'})

def feedback_view(request):
    result = 0
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FeedbackForm(request.POST)
        # check whether it's valid:
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('captcha')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post(settings.GOOGLE_RECAPTCHA_VALIDATE_URL, data=data)
        result = r.json()
        if not result['success']:
            return JsonResponse({'result': 0, 'message': 'Подтвердите, пожалуйста, что Вы - не робот'})
        ''' End reCAPTCHA validation '''
        if form.is_valid():
            # process the data in form.cleaned_data as required
            subject = 'Сообщение с сайта'
            message = request.POST.get('message', '') + chr(13) + ' отправил(а): {}, тел.{}'.format(request.POST.get('client_name', ''),request.POST.get('phone', ''))
            from_email = request.POST.get('sender', '')
            if subject and message and from_email:
                try:
                    result = send_mail(subject, message, from_email, ['vadim.zherdev@gmail.com'])
                except BadHeaderError:
                    return JsonResponse({'result': result, 'message': 'Invalid header found.'})
                return JsonResponse({'result': result, 'message': 'Ваше сообщение отправлено, спасибо!'})
            else:
                return JsonResponse({'result': result, 'message': 'empty fields: "' + subject + '", "' + message + '", "' + from_email})
        else:
            return JsonResponse({'result': result, 'message': form.errors})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = FeedbackForm()
    return JsonResponse({'result': result, 'message': 'request method is not POST'})

def add_to_cart_view(request):
    new_product = int(request.GET.get('product_id', '0'))
    amount = int(request.GET.get('amount', 0))
    date_str = request.GET.get('date', '')
    #print('date_str=', date_str)
    if date_str == '':
        date = None
    else:
        date = datetime.datetime.strptime(date_str, '%Y%m%d')
    #print('new_product=', new_product, ',amount=', amount)
    cart = ShoppingCarts(request)
    #print('date=', date)
    retvalue = cart.add_product(new_product, amount, date)
    cart.save_to_cookies()
    return JsonResponse({'content_html': render_cart(cart, request),
                         'result': retvalue,
                         'cart_date': cart.get_date_text(),
                         'new_amount': cart.get_total_amount()})

def cart_view_full(request):
    return universal_view(request, show_cart=True)

def remove_from_cart_view(request):
    product_id = int(request.GET.get('product_id', 0))
    cart = ShoppingCarts(request)
    cart.remove_item(product_id)
    #cart.reset_date()
    return JsonResponse({'content_html': render_cart(cart, request),
                         'cart_date': cart.get_date_text(),
                         'new_amount': cart.get_total_amount()})
    #JsonResponse({'new_cart_content': generate_cart_content(request, cart)})

def render_cart(cart, request):
    template = loader.get_template('cart_content.html')
    my_html = template.render({'products_in_cart': cart.get_products_in_cart(),
                               'totals': cart.get_totals()},
                              request)
    return my_html

def checkout_view_full(request):
    cart = ShoppingCarts(request)
    if cart.get_totals()['total_cost'] < get_general_settings()['min_order_amount']:
        return redirect('/cart/')
    return universal_view(request, show_checkout=True)

def cookie_confirm_view(request):
    request.session['cookie_warning_confirmed'] = 'whatever'
    #print('whatever saved')
    return JsonResponse({})
