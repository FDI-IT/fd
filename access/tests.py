from django.test import TestCase
from django.test.client import Client

from access.models import Flavor

class FlavorTest(TestCase):
    fixtures = ['access.json']
    
    
#     from access.models import Flavor
    
    test_count = Flavor.objects.all().count()
    print test_count

    def setUp(self):
        self.client = Client()
        self.count = Flavor.objects.count()
        self.test_flavor = Flavor.objects.get(number=8851)
        
    def test_f(self):
        self.assertEqual(self.test_flavor.number,8851)
        self.assertEqual(self.test_flavor.leaf_weights.all().count(), 20)
    
    def test_count(self):
        self.assertEqual(self.count, 40) #WTF 0
    
    def test_review(self):
        response = self.client.get('/access/8851/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['flavor'], self.test_flavor)   
        