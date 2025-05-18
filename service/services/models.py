from django.db import models
from django.core.validators import MaxValueValidator
from clients.models import Clients
from services.tasks import set_price, set_comment
from .receivers import delete_cache_total_sum
from django.db.models.signals import post_delete


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()
    
    def __init__(self, *args, **kwargs):  
        # Инициализатор объекта. Этот метод вызывается при создании нового объекта.
        # Используем __init__ для установки значения переменной __full_price при создании объекта
        super().__init__(*args, **kwargs)  # Вызов __init__ родительского класса, чтобы обеспечить стандартную инициализацию
        self.__full_price = self.full_price  # Сохраняем значение full_price в атрибуте __full_price для последующих сравнений
    
    def save(self, *args, **kwargs):
        # Метод save сохраняет изменения объекта.
        # Здесь мы проверяем, изменился ли full_price с момента последнего сохранения.
        if self.__full_price != self.full_price:
            # Если full_price изменился, то для каждой подписки (subsription) вызываем асинхронную задачу
            for subsription in self.subsriptions.all():
                set_price.delay(subsription.id)  # Запускаем асинхронную задачу для пересчета цены подписки по новому тарифу
                set_comment.delay(subsription.id)  # Запускаем асинхронную задачу для обновления комментария подписки (если требуется)

        # Сохраняем изменения объекта в базу данных
        return super().save(*args, **kwargs)
    
    
class Plan(models.Model):
    PLAN_TYPE = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )
    
    play_type = models.CharField(choices=PLAN_TYPE, max_length=10)
    
    discount_percent = models.PositiveIntegerField(default= 0, validators=[MaxValueValidator(100)])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent
    
    def save(self, *args, **kwargs):
        if self.__discount_percent != self.discount_percent:
            for subsription in self.subsriptions.all():
                set_price.delay(subsription.id)
                set_comment.delay(subsription.id)
                
            
        return super().save(*args, **kwargs)
    
    

class Subsription(models.Model):
    client = models.ForeignKey(Clients, related_name='subsriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subsriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subsriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default = 0)
    comment = models.CharField(default = '', max_length = 50)
    
    def save(self, *args, **kwargs):  # Тут мы предопределяем медот save() 
        creating = not bool(self.id)  # Ссылаемся на self.id который в этом случае id Subsription и если мы изменяем обьект у нас вкомплекте идёт и эта функция
        result = super().save(*args, **kwargs)
        if creating:
            set_price.delay(self.id)
        return result
        
post_delete.connect(delete_cache_total_sum, sender = Subsription)
    