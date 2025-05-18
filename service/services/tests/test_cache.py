from rest_framework.test import APITestCase
from django.core.cache import cache
from django.urls import reverse
from services.models import Subsription
from services.models import Plan, Subsription, Service
from django.contrib.auth.models import User
from clients.models import Clients



class cacheAPITestCase(APITestCase):
        def setUp(self):
            self.user1 = User.objects.create_user(username='Andrue', password='12345', email = 'famas.god1231@gmail.com')
        
            self.cliets1 = Clients.objects.create(user = self.user1, company_name = 'OOOGazKamaz', full_address = 'ASD21')
        
            self.plan1 = Plan.objects.create(play_type = 'student', discount_percent = 20)
        
            self.service1 = Service.objects.create(name = 'Kniga', full_price = 360)
        
            self.subsription1 = Subsription.objects.create(service = self.service1, plan = self.plan1, client = self.cliets1)
            
        def TestRecording_cache(self):  # Тестуруем что кэш записался
            url = reverse('Subsription-list')
            self.client.get(url)
            self.assertIsNotNone(cache.get('price_cache'))
            
        def testUpdatesCreate_cache(self):  # Тестируем что кэш обновился
            url = reverse('Subsription-list')
            self.client.get(url)
            cache.set('price_cache', ['cached'])
            self.subsription2 = Subsription.objects.create(service = self.service2, plan = self.plan2, client = self.cliets2)
            self.assertIsNone(cache.get('price_cache'))