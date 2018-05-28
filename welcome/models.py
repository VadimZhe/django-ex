from django.db import models
from django.utils import translation
from django.utils.formats import date_format

import datetime
import time

# Create your models here.

class PageView(models.Model):
    hostname = models.CharField(max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True)

########################################################

class GeneralSettings(models.Model):
    min_order_amount = models.IntegerField('Минимальная сумма заказа', default=1000)
    max_order_hour = models.IntegerField('Час, после которого нельзя заказать на завтра', default=16)

    def __str__(self):
        return ('Здесь одна строка, редактируйте её, новые не добавляем, эту не удаляем')

    class Meta:
        verbose_name = "Общие настройки"
        verbose_name_plural = "Общие настройки"


class Menus(models.Model):
    day = models.DateField('Дата')
    offered = models.ManyToManyField('Products')

    def week_day_word(self):
        #locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
        translation.activate('ru')
        return date_format(self.day, 'l')

    def compact_date(self):
        return date_format(self.day, 'Ymd')

    def __str__(self):
        return str(self.day)

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

class ShoppingCarts:
    cookie_separator = ';'
    content_cookie_name = 'cart_content'
    date_cookie_name = 'cart_date'
    def __init__(self, request, product_id=0, amount=0, date=None):
        self.request = request
        #request.session.flush() ###########################################################
        full_array = []
        if self.content_cookie_name in request.session:
            full_string = request.session[self.content_cookie_name]
            #print('full_string=', full_string)
            if len(full_string) > 0:
                full_array = list(full_string.split(self.cookie_separator))
        self.date = None
        if self.date_cookie_name in request.session:
            date_str = request.session[self.date_cookie_name]
            if date_str is not None:
                self.date = datetime.datetime.strptime(date_str, '%Y%m%d')
        self.products = list(map(int, full_array[0::3]))
        self.amounts = list(map(int, full_array[1::3]))
        self.dates = []
        for date_str in full_array[2::3]:
            if date_str == '':
                date_to_save = None
            else:
                date_to_save = datetime.datetime.strptime(date_str, '%Y%m%d')
            self.dates.append(date_to_save)
        self.add_product(product_id, amount, date)

    def save_to_cookies(self):
        full_string = ''
        for i in range(len(self.products)):
            if self.dates[i] is None:
                date_to_save = ''
            else:
                date_to_save = date_format(self.dates[i], 'Ymd')
            full_string += str(self.products[i]) + self.cookie_separator \
                           + str(self.amounts[i]) + self.cookie_separator \
                           + date_to_save + self.cookie_separator
        self.request.session[self.content_cookie_name] = full_string[0:-1]
        if self.date is None:
            date_str = None
        else:
            date_str = date_format(self.date, 'Ymd')
        self.request.session[self.date_cookie_name] = date_str
        #print('saved', self.date, 'into', self.date_cookie_name)

    def get_total_amount(self):
        return sum(self.amounts)

    def remove_item(self, product_id):
        position = self.products.index(product_id)
        self.products.pop(position)
        self.amounts.pop(position)
        self.dates.pop(position)
        self.reset_date()
        self.save_to_cookies()

    def get_products_list(self):
        retvalue = []
        for i in range(len(self.products)):
            new_product = Products.objects.get(pk=self.products[i])
            retvalue.append(new_product)
        return retvalue

    def get_products_in_cart(self):
        """ Construct an array of ProductsInCart objects """
        retvalue = list()
        #totals = {'total_amount': 0, 'total_cost': 0}
        #print('products in cart:', len(cart.products))
        for i in range(len(self.products)):
            new_product = Products.objects.get(pk=self.products[i])
            if self.dates[i] is None:
                date_to_save = ''
            else:
                date_to_save = date_format(self.dates[i],'d.m')
            retvalue.append({'product_id': new_product.pk,
                             'product_name': new_product.title,
                             'product_date': date_to_save,
                             'product_price': new_product.price,
                             'amount': self.amounts[i],
                             'cost': new_product.price * self.amounts[i]})
            #totals['total_amount'] += cart.amounts[i]
            #totals['total_cost'] += cart.amounts[i] * new_product.price
            #print('traversing product', new_product.title)
            #print('retvalue=', retvalue)
        return retvalue

    def get_totals(self):
        retvalue = {'total_amount': 0, 'total_cost': 0}
        for i in range(len(self.products)):
            retvalue['total_amount'] += self.amounts[i]
            retvalue['total_cost'] += Products.objects.get(pk=self.products[i]).price * self.amounts[i]
        return retvalue

    def add_product(self, product_id, amount, date):
        #print('date stored is', self.date, ', date passed is', date, 'product id is', product_id)
        # stored date must be equal to passed
        if self.date is not None and date is not None and date != self.date:
            return 0
        # if nothing is stored, but some is passed, keep it
        if self.date is None and date is not None:
            self.date = date
        if product_id > 0:
            if product_id in self.products:
               self.amounts[self.products.index(product_id)] += amount
            else:
                self.products.append(product_id)
                #print(self.products)
                self.amounts.append(amount)
                #print(self.amounts)
                self.dates.append(date)
            #print('returning', amount)
            return amount

    def reset_date(self):
        '''reset cart's date to None if all products in the cart nave no dates'''
        for date in self.dates:
            if date is not None:
                print('date is', date)
                return
        self.date = None
        #print('date has been reset')
        #self.save_to_cookies()

    def expired(self):
        if self.date is None:
            return False
        elif self.date.date() <= datetime.date.today():
            return True
        if self.date.date() == datetime.date.today() + datetime.timedelta(days=1):
            general_settings = GeneralSettings.objects.get(pk=1)
            max_order_hour = general_settings.max_order_hour
            #print('general_settings=', general_settings)
            return datetime.datetime.now().hour >= max_order_hour #TODO: вынести в настройки

    def get_default_delivery_time(self):
        if self.date is None:
            retvalue = datetime.date.today() + datetime.timedelta(days=1)
        else:
            retvalue = self.date
        # 9:30 AM order day (or tomorrow)
        #print('retvalue=', retvalue)
        retvalue = datetime.datetime.combine(retvalue, datetime.time.min)
        retvalue += datetime.timedelta(hours=9, minutes=30)
        return retvalue.strftime('%m-%d-%Y %H:%M')

    def get_date_text(self):
        if self.date is None:
            return ''
        else:
            return ' на ' + date_format(self.date, 'd.m')

class ProductsTypes(models.Model):
    title = models.CharField('Наименование', max_length=50)
    order = models.IntegerField('Порядок', null=False)
    picture = models.ImageField('Картинка', null=True, upload_to='menu/', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип блюд"
        verbose_name_plural = "Типы блюд"

class ProductsSubtypes(models.Model):
    type = models.ForeignKey('ProductsTypes', on_delete=models.PROTECT)
    title = models.CharField('Наименование', max_length=50)
    order = models.IntegerField('Порядок', null=False)
    picture = models.ImageField('Картинка', null=True, upload_to='menu/', blank=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Подтип холодных блюд"
        verbose_name_plural = "Подтипы холодных блюд"

class Products(models.Model):
    type = models.ForeignKey('ProductsTypes', on_delete=models.PROTECT)
    subtype = models.ForeignKey('ProductsSubtypes', on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField('Наименование', max_length=100)
    contents = models.CharField('Состав', max_length=200)
    energy = models.IntegerField('Калорийность')
    weight = models.IntegerField('Вес')
    price = models.FloatField('Цена')
    picture = models.ImageField('Картинка', null=True, upload_to='menu/', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ('title',)

class ProductsInCart(models.Model):

    def __init__(self, product, amount):
        self.product_id = product.pk
        self.product_name = product.title
        self.product_price = product.price
        self.amount = amount

    def get_cost(self):
        print('get_cost:', self.product_price,'*', self.amount)
        return self.product_price * self.amount

    def __str__(self):
        return self.product_name + ', ' + str(self.amount) + ' шт.'

class News(models.Model):
    title = models.CharField('Заголовок', max_length=100)
    icon = models.FileField('Изображение', upload_to='news/')
    full_text = models.TextField('Текст')
    date_created = models.DateField(auto_now=True)
    date_actual = models.DateField('Дата актуализации', null=True, blank=True)
    date_expire = models.DateField('Срок годности', null=True, blank=True)

    class Meta:
        verbose_name='Новость'
        verbose_name_plural='Новости'

    def __str__(self):
        return '{} ({} - {})'.format(self.title, self.date_actual, self.date_expire)

    def get_current_slice(self):
        return self.objects.exclude(date_actual__gt=datetime.datetime.now()).exclude(date_expire__lt=datetime.datetime.now())

class CarouselImages(models.Model):
    image = models.FileField('Изображение', upload_to='carousel/')
    title = models.CharField('Заголовок', max_length=50, null=True)
    text = models.TextField('Текст', null=True)

    def __str__(self):
        return self.image.url[self.image.url.rfind('/')+1:]

    class Meta:
        verbose_name='Картинка для карусели'
        verbose_name_plural='Картинки для карусели'

class Locations(models.Model):
    name = models.CharField('Наименование', unique=True, max_length=20, null=False)
    address = models.CharField('Адрес', max_length=100, null=False)
    hours = models.CharField('Часы работы', max_length=100, null=False)
    latitude = models.FloatField('Широта', null=False)
    longitude = models.FloatField('Долгота', null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='Точка'
        verbose_name_plural='Точки'
