from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.test.client import Client, RequestFactory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.urls import NoReverseMatch

from access.models import Flavor, Ingredient, Formula
from access.views import *

from access.scratch import recalculate_guts
from .urls import urlpatterns

from reversion.models import Version, Revision
from newqc.models import Lot, Retain
from personnel.models import UserProfile

from hazards.models import GHSIngredient, IngredientCategoryInfo
from hazards.tasks import import_initial_data


def show_urls(urllist, depth=0):
    for entry in urllist:
        print("  " * depth, entry.regex.pattern)
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)

#gets complete url list for testing.  removed all ^.  still contains kwargs.
def get_urls(urllist):
    complete_url_list = []
    for entry in urllist:
        if hasattr(entry, 'url_patterns'):
            for sub_url in get_urls(entry.url_patterns):
                complete_url = entry.regex.pattern + sub_url
                complete_url_list.append(complete_url.replace('^','').replace('$',''))
        else:
            complete_url_list.append(entry.regex.pattern)
    return complete_url_list
    
# class testest(TestCase):
#     def testytest(self):
#         flavor_count = Flavor.objects.count()
#         self.assertEqual('foobar', 'foobar')

'''
IMPORTANT:
-ALWAYS prefix individual tests with 'test_'
-When testing http responses, make sure to always add a trailing slash to the url being tested

'''

class PostViewTest(TestCase):

    #not using any fixtures, starting with empty database
    
    def setUp(self):
        self.client = Client()
        
        self.username = 'matta'
        self.email = 'test@test.com'
        self.password = 'fdi'
        self.test_user = User.objects.create_user(self.username, self.email, self.password)
        
        user_profile = UserProfile(user=self.test_user)
        user_profile.save()
        
        #generate the permission objects to add to the new test user; necessary to test certain views
        view_flavor_permission = Permission.objects.get(codename = 'view_flavor')
        change_formula_permission = Permission.objects.get(codename = 'change_formula')
        
        #add the permissions
        self.test_user.user_permissions.add(view_flavor_permission, change_formula_permission)
        
        login = self.client.login(username = self.username, password = self.password)
        
        #ensure that the test user has been successfully logged in
        self.assertEqual(login, True)   
        
        #create test flavor
        self.flavor = Flavor.objects.create(number = 1000,
                        name = "Test Flavor 2",
                        prefix = "TF",
                        natart = "N/A",
                        spg = 0,
                        risk_assessment_group = 1,
                        kosher = "Not Assigned",
                        yield_field = 100,
                        )

        self.ingredient1 = Ingredient.objects.create(
                                 id = 1,
                                 cas = '00-00-01',
                                 product_name = "Test Ingredient 1",
                                 unitprice = Decimal('20.00'),
                                 sulfites_ppm = 0,
                                 package_size = Decimal('0.00'),
                                 minimum_quantity = Decimal('0.00'),
                                 discontinued = False,
                             )
        self.ingredient2 = Ingredient.objects.create(
                                 id = 2,
                                 cas = '00-00-02',
                                 product_name = "Test Ingredient 2",
                                 unitprice = Decimal('10.00'),
                                 sulfites_ppm = 0,
                                 package_size = Decimal('0.00'),
                                 minimum_quantity = Decimal('0.00')
                            )
        self.ingredient3 = Ingredient.objects.create(
                                 id = 1,
                                 cas = '00-00-01',
                                 product_name = "Test Ingredient 1",
                                 unitprice = Decimal('30.00'),
                                 sulfites_ppm = 0,
                                 package_size = Decimal('0.00'),
                                 minimum_quantity = Decimal('0.00'),
                                 discontinued = True,                           
                            )

    def test_add_flavorspec(self):
        #find number of objects before posting to add/save
        flavorspec_count = FlavorSpecification.objects.count()
    
    
        response = self.client.post('/access/1000/spec_list/add/', {'pk': '0',
                                                                    'name': 'test',
                                                                   'specification': 'test_spec',
                                                                   'micro': True})
    

        #self.assertTrue('flavor' in response.context)
        self.assertEqual(response.status_code, 302)
    
        #assert that a flavor specification object was successfully created and saved
        self.assertEqual(FlavorSpecification.objects.count(), flavorspec_count + 1)
        
        
#     def test_reconcile_specs(self):
#         
#         response = self.client.post('/access/%s/reconcile_specs/' % self.flavor.number,
#                                     {'form-TOTAL_FORMS': u'2',
#                                      'form-INITIAL_FORMS': u'0',
#                                      'form-MAX_NUM_FORMS': u'',
#                                      'form-0-name': 'Specific Gravity',
#                                      'form-0-specification': 100,
#                                      'form-1-name': 'Flash Point',
#                                      'form-1-specification': 150,})    
#         
#         #print response
    
    
    def test_retain_creation(self):
        
        retain_count = Retain.objects.count()        
        
        lot = Lot(amount=100,
                  flavor=self.flavor)
        lot.save()
        
        response = self.client.post('/qc/add_retains/?number_of_objects=1', 
                                   {'form-TOTAL_FORMS': '1',
                                    'form-INITIAL_FORMS': '0',
                                    'form-MAX_NUM_FORMS': '',
                                    'form-0-object_number': Retain.get_next_object_number(),
                                    'form-0-flavor_number': self.flavor.number,
                                    'form-0-lot_number': lot.number,})
    
        
        self.assertEqual(response['Location'], 'http://testserver/qc/retains/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Retain.objects.count(), retain_count + 1)


    def test_formula_entry(self):
        
        response = self.client.post('/access/%s/formula_entry/' % self.flavor.number,
                                    {'form-TOTAL_FORMS': '2',
                                     'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '',
                                     'form-0-ingredient_number': self.ingredient1.id,
                                     'form-0-amount': 400,
                                     'form-0-ingredient_pk': self.ingredient1.pk,
                                     'form-1-ingredient_number': self.ingredient2.id,
                                     'form-1-amount': 600,
                                     'form-1-ingredient_pk': self.ingredient2.pk,})    
    
    
#         self.assertEqual(response.status_code, 1999)
    
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/access/1000/recalculate/')

        latest_version = reversion.get_for_object(self.flavor)[0]
        latest_revision = latest_version.revision
        self.assertEqual(latest_revision.comment, 'Old formula: ')
      
        recalculate_guts(self.flavor)
        
        #Ingredient 1: 40%, Unit Price: 20.00
        #Ingredient 2: 60%, Unit Price: 10.00
        #Resulting flavor raw material cost: 20*.4 + 10*.6 = 14.00         
        self.assertEqual(self.flavor.rawmaterialcost, Decimal('14.00'))
        
        latest_version = reversion.get_for_object(self.flavor)[0]
        latest_revision = latest_version.revision
        self.assertEqual(latest_revision.comment, 'Recalculated')
        
        
    def test_raw_material_update(self):
        #need to create two raw materials with the same id and different suppliers/prices
          
        response = self.client.post('/access/ingredient/activate/%s/' % self.ingredient3.pk, {})
        print(response.status_code)
#         print response['Location']
  
        for ing in Ingredient.objects.filter(id=1):
            ing.save()
            print(ing.id, ing.pk, ing.unitprice, ing.discontinued)
          
        #do not use references to the ingredients created above, they do not get updated...  
#         print self.ingredient1.id, self.ingredient1.pk, self.ingredient1.unitprice, self.ingredient1.discontinued
#         print self.ingredient1.id, self.ingredient3.pk, self.ingredient3.unitprice, self.ingredient3.discontinued

        self.assertEqual(Ingredient.objects.get(pk=1).discontinued, True)
        self.assertEqual(Ingredient.objects.get(pk=3).discontinued, False)

        latest_version = reversion.get_for_object(Ingredient.objects.get(pk=1))[0]
        latest_revision = latest_version.revision
        self.assertEqual(latest_revision.comment, 'Old Active Ingredient: DISCONTINUED: Test Ingredient 1, New Active Ingredient: Test Ingredient 1')

    def test_url_responses(self):
        
        test_url_list = [
        '/access/1000/',
        '/access/1000/spec_sheet/',
        '/access/1000/spec_list/',
        '/access/1000/spec_list/edit/%s/' % FlavorSpecification.objects.all()[0].id,
        '/access/1000/spec_list/add/',
        #'/access/1000/spec_list/delete/8/', #302
        '/access/1000/batch_sheet/',
        '/access/1000/formula_entry/',
        '/access/1000/print_review/',
        '/access/1000/reconcile_specs/',
        '/access/tsr/new/',
        #....
        ]
        
        search_urls = [
        '/mysearch/?search_space=flavor&search_string=/',
        '/mysearch/?search_space=ingredient&search_string=/',
        '/mysearch/?search_space=experimental&search_string=/',
        '/mysearch/?search_space=unified&search_string=/',
        '/mysearch/?search_space=purchase_order&search_string=/',
        '/qc/lots/',
        '/qc/rm_retains/',
        '/salesorders/',
        '/salesorders/product/',
        '/salesorders/lineitem/',
        '/batchsheet/',
        
        ]
        
        print("Testing URLS...")
        for url in test_url_list + search_urls:
            response = self.client.get(url)
            print(url) 
            self.assertEqual(response.status_code, 200)
        
    def test_reversion(self):
        pass
  
class HttpResponseTest(TestCase):

    #fixtures = ['access.json']
     
    def setUp(self):
        self.client = Client()

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

        
class HazardTest2(TestCase):
      
    #fixtures = ['hazard_data.json']
      
    def setUp(self):
    
        self.testflavor = Flavor.objects.create(number = 9999,
                        name = "Test Flavor 2",
                        prefix = "TF",
                        natart = "N/A",
                        spg = 0,
                        risk_assessment_group = 1,
                        kosher = "Not Assigned",
                        yield_field = 100,
                        )

        import_initial_data()

        ghs_component1 = GHSIngredient.objects.create(
                            cas = '00-00-01')

        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component1,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='TOSTSingleHazard')\
                            .get(category='3NE')
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component1,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='TOSTSingleHazard')\
                            .get(category='3RI')
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component1,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityOral')\
                            .get(category='5'),
            ld50 = 5000
        )


        ghs_component2 = GHSIngredient.objects.create(
                            cas = '00-00-02',)

        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component2,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityOral')\
                            .get(category='4'),
            ld50 = 500
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component2,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='SkinCorrosionHazard')\
                            .get(category='1A')
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component2,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityDermal')\
                            .get(category='4'),
            ld50 = 1500
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component2,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='EyeDamageHazard')\
                            .get(category='1')
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component2,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='SkinSensitizationHazard')\
                            .get(category='1B')
        )


        ghs_component3 = GHSIngredient.objects.create(
                            cas = '00-00-03',)

        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component3,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityOral')\
                            .get(category='3'),
            ld50 = 75
        )
        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component3,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityDermal')\
                            .get(category='3'),
            ld50 = 1000
        )



        ghs_component4 = GHSIngredient.objects.create(
                            cas = '00-00-04',)

        IngredientCategoryInfo.objects.create(
            ingredient = ghs_component4,
            category = HazardCategory.objects.filter(hazard_class__python_class_name='TOSTSingleHazard')\
                            .get(category='3RI')
        )
          
        ing_component1 = Ingredient.objects.create(cas = '00-00-01',
                             product_name = "Test Ingredient 1",
                             unitprice = Decimal('10.00'),
                             sulfites_ppm = 0,
                             package_size = Decimal('0.00'),
                             minimum_quantity = Decimal('0.00')
                             )
        ing_component2 = Ingredient.objects.create(cas = '00-00-02',
                             product_name = "Test Ingredient 2",
                             unitprice = Decimal('10.00'),
                             sulfites_ppm = 0,
                             package_size = Decimal('0.00'),
                             minimum_quantity = Decimal('0.00')
                             )
        ing_component3 = Ingredient.objects.create(cas = '00-00-03',
                             product_name = "Test Ingredient 3",
                             unitprice = Decimal('10.00'),
                             sulfites_ppm = 0,
                             package_size = Decimal('0.00'),
                             minimum_quantity = Decimal('0.00')
                             )
        ing_component4 = Ingredient.objects.create(cas = '00-00-04',
                             product_name = "Test Ingredient 4",
                             unitprice = Decimal('10.00'),
                             sulfites_ppm = 0,
                             package_size = Decimal('0.00'),
                             minimum_quantity = Decimal('0.00')
                             )
          
        formula1 = Formula.objects.create(flavor = self.testflavor,
                  ingredient = ing_component1,
                  acc_flavor = self.testflavor.number,
                  acc_ingredient = ing_component1.id,
                  amount = 5
                  )
        formula2 = Formula.objects.create(flavor = self.testflavor,
                  ingredient = ing_component2,
                  acc_flavor = self.testflavor.number,
                  acc_ingredient = ing_component2.id,
                  amount = 40
                  )
        formula3 = Formula.objects.create(flavor = self.testflavor,
                  ingredient = ing_component3,
                  acc_flavor = self.testflavor.number,
                  acc_ingredient = ing_component3.id,
                  amount = 500
                  )
        formula4 = Formula.objects.create(flavor = self.testflavor,
                  ingredient = ing_component4,
                  acc_flavor = self.testflavor.number,
                  acc_ingredient = ing_component4.id,
                  amount = 455
                  )
          
        recalculate_guts(self.testflavor)

        self.hazards = self.testflavor.set_hazards()

    def test_ld50s(self):
        self.assertEqual(round(self.hazards['oral_ld50']), 81)
        self.assertEqual(round(self.hazards['dermal_ld50']), 1035)

    def test_hazards(self):
        #print "Hazard Dict: %s\n" % self.hazards

        self.assertEqual(self.hazards['AcuteToxicityDermal'], '4')
        self.assertEqual(self.hazards['AcuteToxicityOral'], '3')
        self.assertEqual(self.hazards['EyeDamageHazard'], '1')
        self.assertEqual(self.hazards['SkinCorrosionHazard'], '2')
        self.assertEqual(self.hazards['SkinSensitizationHazard'], '1B')
        self.assertEqual(self.hazards['TOSTSingleHazard'], '3RI')

        #print "Flavor Hazard Set:"
        #print self.testflavor.hazard_set.all()



        

        
    
        
        
    
    
        
        