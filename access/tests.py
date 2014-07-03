from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client, RequestFactory


from access.models import Flavor
from access.controller import HazardAccumulator
from access.views import *

# class FlavorTest(TestCase):
#     fixtures = ['access.json']
#     
#     
# #     from access.models import Flavor
# #     
# #     test_count = Flavor.objects.all().count()
# #     print test_count
# # 
# #     def setUp(self):
# #         self.client = Client()
# #         self.count = Flavor.objects.count()
# #         self.test_flavor = Flavor.objects.get(number=8851)
# #         
# #     def test_f(self):
# #         self.assertEqual(self.test_flavor.number,8851)
# #         self.assertEqual(self.test_flavor.leaf_weights.all().count(), 20)
# #     
# #     def test_count(self):
# #         self.assertEqual(self.count, 40) #WTF 0
# #     
# #     def test_review(self):
# #         response = self.client.get('/access/8851/', follow=True)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertEqual(response.context['flavor'], self.test_flavor)   
#         
        

'''
IMPORTANT:
-ALWAYS prefix individual tests with 'test_'
-When testing http responses, make sure to always add a trailing slash to the url being tested

'''

class PostViewTest(TestCase):
    fixtures = ['emptydb.json']
     
    def setUp(self):
        self.client = Client()
        self.client.login(username='matta', password='fdi')
        #self.factory = RequestFactory()
        #self.user = User.objects.create_user(
        #    username='matta_test', email='matta@flavordynamics.com', password='fdi')
        self.flavor = Flavor.objects.get(number=8851)  
        
    '''
    might wanna try using assertFormError:
    
    self.assertFormError(response, 'form', 'something', 'message')
        'form' is the context variable name for form, 
        'something' is the field name
        'message' is expected text of validation error
        
    '''

#     def test_add_rawmaterial(self):
#         response = self.client.post('/access/new_rm/basic/', {'pk': 1,
#                                                               'art_nati': 'Nat',
#                                                                'product_name': 'Test Ingredient',
#                                                                'solubility': 'Water',
#                                                                'unitprice': 1,
#                                                                'purchase_price_update': '2014-06-26',
#                                                                'supplier': 'Foobar',
#                                                                'package_size': 1,
#                                                                'minimum_quantity': 2,
#                                                                'fob_point': 3,
#                                                                'lead_time': 4,
#                                                                'lastkoshdt': '1990-01-01',
#                                                                'hazardous': False,
#                                                                'microsensitive': '',
#                                                                'prop65': False,
#                                                                'nutri': False,
#                                                                'sulfites_ppm': 5,
#                                                                'allergen': '',
#                                                                })
#         
#         self.assertEqual(response.status_code, 302)

    def test_add_flavorspec(self):
        #self.client.login(username='matta', password='fdi')
        
        #find number of objects before posting to add/save
        flavorspec_count = FlavorSpecification.objects.count()
        
        response = self.client.post('/access/8851/spec_list/add/', {'pk': '0',
                                                                    'name': 'test', 
                                                                   'specification': 'test_spec',
                                                                   'micro': True}) 
                                                           
        #self.assertTrue('flavor' in response.context)
        self.assertEqual(response.status_code, 302)
        
        #assert that a flavorspecification object was successfully created and saved        
        self.assertEqual(FlavorSpecification.objects.count(), flavorspec_count + 1)
        
        
class HttpResponseTest(TestCase):
    #fixtures = ['access.json'] this json file is outdated and using it will result in an error 
                                    #FieldDoesNotExist: ExperimentalLog has no field named u'flavor_coat'

    fixtures = ['testdb.json']
     
    def setUp(self):
        self.client = Client()
        #self.factory = RequestFactory()
        #self.user = User.objects.create_user(
        #    username='matta_test', email='matta@flavordynamics.com', password='fdi')
        self.flavor = Flavor.objects.get(number=8851)
    
              
    def test_flavorview(self):
        
        #test /access/
        response = self.client.post('/access/') 
        self.assertEqual(response.status_code, 200)

        
        #test /access/9999, make sure that non-existent flavors throw a 404
        response = self.client.get('/access/9999/')
        self.assertEqual(response.status_code, 404)
        
        #test /access/1000
        response = self.client.get('/access/8851/') 
        self.assertEqual(response.status_code, 200)
        
        #check that there is a 'flavor' key in context
        self.assertTrue('flavor' in response.context)
        
        #make sure the flavor has number 1000
        self.assertEqual(response.context['flavor'].number, 8851)
