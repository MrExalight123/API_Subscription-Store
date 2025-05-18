
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
import json
from django.contrib.auth.models import User
from services.models import Subsription
from clients.models import Clients
from services.models import Plan, Subsription, Service
from ..serializers import SubsriptionSerializers
from ..tasks import set_price
from django.core.cache import cache




class  SubsriptionApiTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Andrue', password='12345', email = 'famas.god1231@gmail.com')
        self.user2 = User.objects.create_user(username='Maxsim', password='54321', email = 'famas.god12345@gmail.com')
        
        self.cliets1 = Clients.objects.create(user = self.user1, company_name = 'OOOGazKamaz', full_address = 'ASD21')
        self.cliets2 = Clients.objects.create(user = self.user2, company_name = 'OOONefyiMnoga', full_address = 'QWERTY1231')
        
        self.plan1 = Plan.objects.create(play_type = 'student', discount_percent = 20)
        self.plan2 = Plan.objects.create(play_type = 'discount', discount_percent = 0)
        
        self.service1 = Service.objects.create(name = 'Kniga', full_price = 360)
        self.service2 = Service.objects.create(name = 'Game', full_price = 890)
        
        self.subsription1 = Subsription.objects.create(service = self.service1, plan = self.plan1, client = self.cliets1)
        self.subsription2 = Subsription.objects.create(service = self.service2, plan = self.plan2, client = self.cliets2)
        
        cache.clear()  # Чистим кэш чтобы расчёт пошел, ибо у нас только после этого начнеться пересчет
        
    def test_get(self):
        set_price.apply(args=[self.subsription1.id])  # Принудительно запускаем задачи ибо celery не успевает посчитать и тест выдаёт ошибку
        set_price.apply(args=[self.subsription2.id])
        url = reverse('Subsription-list')
        response = self.client.get(url)
        subs = Subsription.objects.all()
        serializers_data = SubsriptionSerializers(subs, many = True).data
        sum = 1178
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['result'], serializers_data)
        self.assertEqual(response.data['total_amout'], sum)
        
        
    def test_no_create(self):
        url = reverse('Subsription-list')
        response = self.client.get(url)
        data = {
            'id' : self.subsription1.id,
            'plan_id' : self.plan1.id,
            'client_name' : 'OOOSosisko',
            'email' : 'famas.god123456@gmail.com',
            'plan' : {
                'id' : self.plan1.id,
                'play_type' : 'student',
                'discount_percent' : 20,
            },
            'price' : 120,
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data = json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual(Subsription.objects.all().count(), 2)
        
    def test_no_delete(self):
        url = reverse('Subsription-detail', args=(self.subsription1.id,))
        response = self.client.delete(url, content_type = 'application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual(Subsription.objects.all().count(), 2)
        
    def test_no_put(self):
        set_price.apply(args=[self.subsription1.id])  # Принудительно запускаем задачи ибо celery не успевает посчитать и тест выдаёт ошибку
        set_price.apply(args=[self.subsription2.id])
        url = reverse('Subsription-detail', args=(self.subsription1.id,))
        data = {
            'id' : self.subsription1.id,
            'plan_id' : self.plan1.id,
            'client_name' : 'OOOGazKamaz',
            'email' : 'famas.god1231@gmail.com',
            'plan' : {
                'id' : self.plan1.id,
                'play_type' : 'student',
                'discount_percent' : 20,
            },
            'price' : 260,
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data = json_data, content_type = 'application/json')
        self.subsription1.refresh_from_db()
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual(self.subsription1.price, 288)  # 288 потомучто скида 20 процентов
        