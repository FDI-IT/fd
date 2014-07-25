from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.test.client import Client, RequestFactory

from access.models import Flavor, Ingredient, Formula
from access.controller import HazardAccumulator
from access.views import *

from access.scratch import recalculate_guts

from hazard_calculator.models import GHSIngredient


'''
IMPORTANT:
-ALWAYS prefix individual tests with 'test_'
-When testing http responses, make sure to always add a trailing slash to the url being tested

'''

class PostViewTest(TestCase):
    #fixtures = ['access.json']
     
    def setUp(self):
        self.client = Client()
        self.client.login(username='matta', password='fdi')

        self.flavor = Flavor.objects.create(number = 1000,
                        name = "Test Flavor 2",
                        prefix = "TF",
                        natart = "N/A",
                        spg = 0,
                        risk_assessment_group = 1,
                        kosher = "Not Assigned",
                        yield_field = 100,
                        )
             
        
    '''
    might wanna try using assertFormError:
    
    self.assertFormError(response, 'form', 'something', 'message')
        'form' is the context variable name for form, 
        'something' is the field name
        'message' is expected text of validation error
        
    '''


    def test_add_flavorspec(self):
        #self.client.login(username='matta', password='fdi')
        
        #find number of objects before posting to add/save
        flavorspec_count = FlavorSpecification.objects.count()

        
        response = self.client.post('/access/1000/spec_list/add/', {'pk': '0',
                                                                    'name': 'test', 
                                                                   'specification': 'test_spec',
                                                                   'micro': True}) 
                                                           
        #self.assertTrue('flavor' in response.context)
        self.assertEqual(response.status_code, 302)
        
        #assert that a flavorspecification object was successfully created and saved     
        #TODO   
        #self.assertEqual(FlavorSpecification.objects.count(), flavorspec_count + 1)
        
        
class HttpResponseTest(TestCase):

    #fixtures = ['access.json']
     
    def setUp(self):
        self.client = Client()
        #self.factory = RequestFactory()
        #self.user = User.objects.create_user(
        #    username='matta_test', email='matta@flavordynamics.com', password='fdi')
        self.testflavor = Flavor.objects.create(number = 1000,
                        name = "Test Flavor 2",
                        prefix = "TF",
                        natart = "N/A",
                        spg = 0,
                        risk_assessment_group = 1,
                        kosher = "Not Assigned",
                        yield_field = 100,
                        )
            
    
              
    def test_flavorview(self):
        
        #test /access/
        response = self.client.post('/access/') 
        self.assertEqual(response.status_code, 200)

        
        #test /access/9999, make sure that non-existent flavors throw a 404
        response = self.client.get('/access/9999/')
        self.assertEqual(response.status_code, 404)
        
        #test /access/1000
        response = self.client.get('/access/1000/') 
        self.assertEqual(response.status_code, 200)
        
        #check that there is a 'flavor' key in context
        self.assertTrue('flavor' in response.context)
        
        #make sure the flavor has number 1000
        self.assertEqual(response.context['flavor'].number, 1000)


        
# class HazardTest2(TransactionTestCase):
#     
#     #fixtures = ['hazard_data.json']
#     
#     def setUp(self):
#         self.testflavor = Flavor.objects.create(number = 9999,
#                         name = "Test Flavor 2",
#                         prefix = "TF",
#                         natart = "N/A",
#                         spg = 0,
#                         risk_assessment_group = 1,
#                         kosher = "Not Assigned",
#                         yield_field = 100,
#                         )
#             
#         ghs_component1 = GHSIngredient.objects.create(
#                             cas = '00-00-01',
#                             oral_ld50 = 5000,
#                             tost_single_hazard = '3-NE, 3-RI')
#         ghs_component2 = GHSIngredient.objects.create(
#                             cas = '00-00-02',
#                             oral_ld50 = 500,
#                             dermal_ld50 = 1500,
#                             eye_damage_hazard = '1',
#                             skin_corrosion_hazard = '1A',
#                             skin_sensitization_hazard = '1B',
#                             aspiration_hazard = '1',)
#         ghs_component3 = GHSIngredient.objects.create(
#                             cas = '00-00-03',
#                             oral_ld50 = 75,
#                             dermal_ld50 = 1000)
#         ghs_component4 = GHSIngredient.objects.create(
#                             cas = '00-00-04',
#                             tost_single_hazard = '3-RI',
#                             aspiration_hazard = '1',)
#         
#         
#         ing_component1 = Ingredient.objects.create(cas = '00-00-01',
#                              product_name = "Test Ingredient 1",
#                              unitprice = Decimal('10.00'),
#                              sulfites_ppm = 0,
#                              package_size = Decimal('0.00'),
#                              minimum_quantity = Decimal('0.00')
#                              )
#         ing_component2 = Ingredient.objects.create(cas = '00-00-02',
#                              product_name = "Test Ingredient 2",
#                              unitprice = Decimal('10.00'),
#                              sulfites_ppm = 0,
#                              package_size = Decimal('0.00'),
#                              minimum_quantity = Decimal('0.00')
#                              )
#         ing_component3 = Ingredient.objects.create(cas = '00-00-03',
#                              product_name = "Test Ingredient 3",
#                              unitprice = Decimal('10.00'),
#                              sulfites_ppm = 0,
#                              package_size = Decimal('0.00'),
#                              minimum_quantity = Decimal('0.00')
#                              )
#         ing_component4 = Ingredient.objects.create(cas = '00-00-04',
#                              product_name = "Test Ingredient 4",
#                              unitprice = Decimal('10.00'),
#                              sulfites_ppm = 0,
#                              package_size = Decimal('0.00'),
#                              minimum_quantity = Decimal('0.00')
#                              )
#         
#         formula1 = Formula.objects.create(flavor = self.testflavor,
#                   ingredient = ing_component1,
#                   acc_flavor = self.testflavor.number,
#                   acc_ingredient = ing_component1.id,
#                   amount = 5
#                   )
#         formula2 = Formula.objects.create(flavor = self.testflavor,
#                   ingredient = ing_component2,
#                   acc_flavor = self.testflavor.number,
#                   acc_ingredient = ing_component2.id,
#                   amount = 40
#                   )
#         formula3 = Formula.objects.create(flavor = self.testflavor,
#                   ingredient = ing_component3,
#                   acc_flavor = self.testflavor.number,
#                   acc_ingredient = ing_component3.id,
#                   amount = 500
#                   )
#         formula4 = Formula.objects.create(flavor = self.testflavor,
#                   ingredient = ing_component4,
#                   acc_flavor = self.testflavor.number,
#                   acc_ingredient = ing_component4.id,
#                   amount = 455
#                   )
#         
#         recalculate_guts(self.testflavor)
#         
#         self.hazards = self.testflavor.get_hazards()
#         #print self.hazards
#         
#     def test_ld50s(self):
#         self.assertEqual(round(self.hazards['oral_ld50']), 81)
#         self.assertEqual(round(self.hazards['dermal_ld50']), 1035)
#          
#     def test_hazards(self):
#         self.assertEqual(self.hazards['acute_hazard_dermal'], '4')
#         self.assertEqual(self.hazards['acute_hazard_oral'], '3')
#         self.assertEqual(self.hazards['eye_damage_hazard'], '1')
#         self.assertEqual(self.hazards['skin_corrosion_hazard'], '2')
#         self.assertEqual(self.hazards['skin_sensitization_hazard'], '1B')
#         self.assertEqual(self.hazards['tost_single_hazard'], '3-RI')
        

        
# #MIXTURE EXAMPLE 1 - from GHS packet   
# class HazardTest1(TestCase):
#     fixtures = ['testdata.json']
#     
#     def setUp(self):
#         self.count = Flavor.objects.count()
#         self.flavor = Flavor.objects.get(number=1000)
#         self.accumulator = HazardAccumulator(self.flavor)
#         self.subhazard_dict = self.accumulator.subhazard_dict
#         self.hazard_dict = self.accumulator.get_hazard_dict()
#     
#     #ensure that there is only one flavor in the testdata fixture    
#     def test_count(self): 
#         self.assertEqual(self.count, 1)
#         
# 
#     #testing various properties to ensure the hazardaccumulator is working correctly  
#     def test_ld50s(self): 
#         self.assertEqual(round(self.subhazard_dict['dermal_ld50']), 24286)
#         
#     def test_eye_category(self):
#         self.assertEqual(self.hazard_dict['eye_damage_hazard'], '2A')
#         

        

        
    
        
        
    
    
        
        