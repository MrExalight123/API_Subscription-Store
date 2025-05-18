import datetime
from celery import shared_task
from django.db.models import F
from celery_singleton import Singleton
import time
from django.db import transaction

from django.core.cache import cache
from django.conf import settings




# Celery tasks.py в docker просто так не обновляються надо каждый раз его перезапускать


@shared_task(base=Singleton)  # @shared_task Обязателен когда мы пишим воркеры,
                              # а этот аргумент делает так чтобы придерживалось патерна Singleton(Тоесть только одна ориг. версия может работать и у неё не может быть копий)
                              # Это делаеться для того чтобы при изменении одного обьектка несколько раз у нас не стагалась очередь а было активно только последния изменения
                               
def set_price(subsription_id):
    from services.models import Subsription
    with transaction.atomic():  # Эта тразнакция забирает себе Subsription и не одаст его не кому пока не вы высчитавает все данные
    
        subsription = Subsription.objects.select_for_update().filter(id=subsription_id).annotate(annotate_price = F('service__full_price') - F('service__full_price') * 
                                                                                 F('plan__discount_percent') / 100.00).first()  # fisrt() Здесь нужен чтобы не допускать дубликатов
                                                                                                                                # При расчёте
    
    
        subsription.price = subsription.annotate_price
        subsription.save()
    cache.delete(settings.PPRICE_CACHE_NAME)  # Здесь возникает вопрос а на кой нам здесь 
    
@shared_task(base=Singleton)
def set_comment(subsription_id):
    from services.models import Subsription
    
    with transaction.atomic():  # with тут кста для того чтобы открывать трназакцию 'with' Это буквально открытия чего либо
        
        subsription = Subsription.objects.select_for_update().get(id=subsription_id)
    
        subsription.commeent = str(datetime.datetime.now())
        subsription.save()
    cache.delete(settings.PPRICE_CACHE_NAME)