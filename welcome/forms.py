from datetimewidget.widgets import DateTimeWidget

from django import forms

from .models import Locations

class FeedbackForm(forms.Form):
    client_name = forms.CharField(label='Ваше имя', max_length=50)
    sender = forms.EmailField(label='E-mail')
    phone = forms.CharField(label='Телефон', max_length=15)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea)

#class CheckoutForm(forms.Form):
#    client_name = forms.CharField(label='Ваше имя', max_length=50, initial='Вадим')
#    sender = forms.EmailField(label='E-mail', initial='vadim.zherdev@gmail.com')
#    phone = forms.CharField(label='Телефон', max_length=15, initial='+79112148436')
#    shipping = forms.ChoiceField(label='Доставка',
#                                 widget=forms.RadioSelect,
#                                 choices=((1, "Мне нужна доставка"),
#                                          (2, "Я заберу сам из ресторана")),
#                                 required=False)
#    address = forms.CharField(label='Адрес', max_length=200, initial='Ленсовета, 10')
#    address2 = forms.CharField(label='Адрес', max_length=200, initial='Десятый подъезд', required=False)
#    delivery_time = forms.DateTimeField(label='Время',
#                                        #widget=DateTimeWidget(usel10n=True, bootstrap_version=3),
#                                        required=True)
#    cafe_to_pick_up = forms.ModelChoiceField(queryset=Locations.objects.all(), required=False)
#    flatware = forms.IntegerField(label='Приборы', required=False, initial=0)
#    hot_delivery = forms.BooleanField(label='Доставка в горячем виде', required=False)
#    payment_method = forms.ChoiceField(label="Способ оплаты",
#                                       widget=forms.RadioSelect,
#                                       choices=((1, "Оплата наличными (водителю или в кассе Fresh Point)"),
#                                                (2, 'По безналичному расчету (от юридического лица)')))
#
#    class Meta:
#        #model = yourModel
#        widgets = {
#            #Use localization and bootstrap 3
#            'datetime': DateTimeWidget(attrs={'id':"yourdatetimeid"}, usel10n = True, bootstrap_version=3)
#        }

