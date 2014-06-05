from django.test import TestCase
from django.test.client import Client


from access.models import Flavor
from access.controller import HazardAccumulator

class FlavorTest(TestCase):
    fixtures = ['access.json']
    
    
#     from access.models import Flavor
#     
#     test_count = Flavor.objects.all().count()
#     print test_count
# 
#     def setUp(self):
#         self.client = Client()
#         self.count = Flavor.objects.count()
#         self.test_flavor = Flavor.objects.get(number=8851)
#         
#     def test_f(self):
#         self.assertEqual(self.test_flavor.number,8851)
#         self.assertEqual(self.test_flavor.leaf_weights.all().count(), 20)
#     
#     def test_count(self):
#         self.assertEqual(self.count, 40) #WTF 0
#     
#     def test_review(self):
#         response = self.client.get('/access/8851/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['flavor'], self.test_flavor)   
        
        
        
#MIXTURE EXAMPLE 1 - from GHS packet   
class HazardTest1(TestCase):
    fixtures = ['testdata2.json']
    
    def setUp(self):
        self.count = Flavor.objects.count()
        self.flavor = Flavor.objects.get(number=1000)
        self.accumulator = HazardAccumulator(self.flavor)
        self.subhazard_dict = self.accumulator.subhazard_dict
        self.hazard_dict = self.accumulator.get_hazard_dict()
    
    #ensure that there is only one flavor in the testdata fixture    
    def test_count(self): 
        self.assertEqual(self.count, 1)
        

    #testing various properties to ensure the hazardaccumulator is working correctly  
    def test_ld50s(self): 
        self.assertEqual(round(self.subhazard_dict['dermal_ld50']), 24286)
        
    def test_eye_category(self):
        self.assertEqual(self.hazard_dict['eye_damage_hazard'], '2A')
        
        
class HazardTest2(TestCase): 
    fixtures = ['testdata2.json']
    
    def setUp(self):
        self.count = Flavor.objects.count()
        self.flavor = Flavor.objects.get(number=1001)
        self.accumulator = HazardAccumulator(self.flavor)
        self.subhazard_dict = self.accumulator.subhazard_dict
        self.hazard_dict = self.accumulator.get_hazard_dict()
        
    def test_count(self):
        self.assertEqual(self.count, 1)
        
    def test_ld50s(self):
        self.assertEqual(round(self.subhazard_dict['oral_ld50']), 81)
        self.assertEqual(round(self.subhazard_dict['dermal_ld50']), 1035)
        
    def test_hazards(self):
        self.assertEqual(self.hazard_dict['acute_hazard_dermal'], '4')
        self.assertEqual(self.hazard_dict['acute_hazard_oral'], '3')
        self.assertEqual(self.hazard_dict['eye_damage_hazard'], '1')
        self.assertEqual(self.hazard_dict['skin_corrosion_hazard'], '2')
        self.assertEqual(self.hazard_dict['skin_sensitization_hazard'], '1B')

        

        
    
        
        
    
    
        
        