from django.test import TestCase
from django.test.client import Client

from access.models import *

class FlavorTest(TestCase):
    fixtures =['test_data.json',]
    test_flavor = Flavor.objects.get(number=9700)
    def setUp(self):
        self.client = Client()
        
    def test_f(self):
        self.assertEqual(self.test_flavor.number,9700)
        self.assertEqual(self.test_flavor.leaf_weights.all().count(), 38)
    
    
    def test_review(self):
        response = self.client.get('/access/9700/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['flavor'], self.test_flavor)
        
        