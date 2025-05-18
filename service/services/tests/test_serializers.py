from django.test import TestCase
from services.models import Plan, Subsription, Service
from services.serializers import PlanSerializers, SubsriptionSerializers
from clients.models import Clients
from django.contrib.auth.models import User
import json


class PlanSerializersTestCase(TestCase):
    def setUp(self):
        self.plan1 = Plan.objects.create(play_type = 'student', discount_percent = 20)
        
    def test_ok(self):
        Serializers1 = PlanSerializers(self.plan1).data
        Serializers2 = {
            'id' : self.plan1.id,
            'play_type' : 'student',
            'discount_percent' : 20
        }
        
        self.assertEqual(Serializers1, Serializers2)
        
class SubsriptionSerializersTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Andrue', password='12345', email = 'famas.god1231@gmail.com')
        self.user2 = User.objects.create_user(username='Maxsim', password='54321', email = 'famas.god12345@gmail.com')
        
        self.cliets1 = Clients.objects.create(user = self.user1, company_name = 'OOOGazKamaz', full_address = 'ASD21')
        self.cliets2 = Clients.objects.create(user = self.user2, company_name = 'OOONefyiMnoga', full_address = 'QWERTY1231')
        
        self.plan1 = Plan.objects.create(play_type = 'student', discount_percent = 20)
        self.plan2 = Plan.objects.create(play_type = 'discount', discount_percent = 0)
        
        self.service1 = Service.objects.create(name = 'Kniga', full_price = 0)
        self.service2 = Service.objects.create(name = 'Game', full_price = 0)
        
        
        
        self.subsription1 = Subsription.objects.create(service = self.service1, plan = self.plan1, client = self.cliets1, price = 360)
        self.subsription2 = Subsription.objects.create(service = self.service2, plan = self.plan2, client = self.cliets2, price = 890)

        
        
    def test_ok(self):
        subs = Subsription.objects.all()
        Serializers1 = SubsriptionSerializers(subs, many = True).data
        Serializers1_dict = json.loads(json.dumps(Serializers1))
        Serializers2 = [{
            'id' : self.subsription1.id,
            'plan_id' : self.plan1.id,
            'client_name' : 'OOOGazKamaz',
            'email' : 'famas.god1231@gmail.com',
            'plan' : {
                'id' : self.plan1.id,
                'play_type' : 'student',
                'discount_percent' : 20,
            },
            'price' : 360,
        }, {
            'id' : self.subsription2.id,
            'plan_id' : self.plan2.id,
            'client_name' : 'OOONefyiMnoga',
            'email' : 'famas.god12345@gmail.com',
            'plan' : {
                'id' : self.plan2.id,
                'play_type' : 'discount',
                'discount_percent' : 0,
            },
            'price' : 890,
        }]
        
        self.assertEqual(Serializers1_dict, Serializers2)
        
    
class PlanSerializersNoInfoTestCase(TestCase):
    def test_ok(self):
        serializers1 = PlanSerializers(Plan.objects.none(), many = True).data
        self.assertEqual(serializers1, [])
        
class SubsriptionSerializersNoInfoTestCase(TestCase):
    def test_ok(self):
        serializers1 = SubsriptionSerializers(Subsription.objects.none(), many = True).data
        self.assertEqual(serializers1, [])