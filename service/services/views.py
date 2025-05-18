from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from services.models import Subsription
from services.serializers import SubsriptionSerializers
from django.db.models import Prefetch
from clients.models import Clients
from django.db.models import Sum, F  # F Здесь нужно для того чтобы позволять вычислять а самой анотации
from django.core.cache import cache
from django.conf import settings


class SubsriptionView(ReadOnlyModelViewSet):
#   queryset = Subsription.objects.all().prefetch_related('client').prefetch_related('client__user')  # prefetch_related Изпользуюеться когда надо сделать 
                                                                                                      # связанных данных из той же базы данных
                                                                                                      # И потом два запроса соеденяються в одине при помощи python
                                                                                                      # а select_related соеденяет две таблица и берёт и них данные поэтому
                                                                                                      # его изпользуют когда идёт связь OneToOne или форенгей к одной записи
                                                                                                      # Ибо если записей много лучше изпользовать prefetch_related и это будет оптимизированией
                                                                                                      # А если будет одна запись то соеденить будет более оптимизированно
                                                                                                      
                                                                                                      # Но почему это неэфективно?
                                                                                                      # А потому что мы фактически берём все данные из user вместо того что нам надо
                                                                                                      # А нам из user нужен только email. Ниже показано как фиксить
                                                                                                      
    queryset = Subsription.objects.all().prefetch_related(
        'plan', 'service',
        Prefetch('client', queryset=Clients.objects.all().select_related('user').only('company_name',
                                                                                      'user__email',))  # only позволяет выбрать из в данным случае user только несколько полей
                                                                                                        # А 'client' В начале нужен для того чтобы связаеться через Subsription по client
                                                                                                        # А потом добраться в user 
        )
                                                                                                                                                                                                                                                            
    serializer_class = SubsriptionSerializers
    
    def list(self, request, *args, **kwargs):  # Тут мы предопределяем list и добавляем в него свою логику в данном случае высчитаваем всю сумму price
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        price_cache = cache.get(settings.PRICE_CACHE_NAME)
        
        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60 * 60)
        
        response_data = {'result' : response.data}
        response_data['total_amout'] = total_price
        response.data = response_data 
        
        return response