from fd.access.models import Ingredient
import Queue

solution_percent_tokens = (
                           '25%',
                           '10%',
                           '5%',
                           '1%',
                           '.1%',
                           '0.1%',
                           )
solvent_tokens = (
                  'pg',
                  'etoh',
                  'triacetin',
                  'soybean oil',
                  'neoboo',
                  'water',
                  )
supplier_codes = (
                  'abt',
                  'cna',
                  'kerry',
                  'vigon',
                  )

def simulate_solution_names():
    
    for 

def read_lorem():
    loremfile = open('/home/stachurski/loremipsum.txt', 'r')
    lorem_line = loremfile.read()
    lorems = lorem_line.split(',')
    lorems = lorems[0:len(lorems)-1]
    q = Queue.Queue()
    for word in lorems:
        q.put(word)
        
    for f in Flavor.objects.all():
        lorem_one = q.get()
        lorem_two = q.get()
        lorem_three = q.get()
        lorem_four = q.get()
        print f
        f.name = "%s %s" % (lorem_one, lorem_two)
        f.type = "Flavor"
        f.productmemo = "%s %s %s %s" % (lorem_one, lorem_two, lorem_three, lorem_four)
        f.prefix = "FL"
        f.save()
        
        q.put(lorem_one)
        q.put(lorem_two)
        q.put(lorem_three)
        q.put(lorem_four)
        
        print f
        
    for rm in Ingredient.objects.all():
        lorem_one = q.get()
        
        lorem_two = q.get()
        lorem_three = q.get()
        
        rm.product_name = "%s %s" % (lorem_one, lorem_two)
        rm.part_name2 = "%s" % (lorem_three)
        rm.description = "%s %s %s" % (lorem_one, lorem_two, lorem_three)
        rm.suppliercode = "FDI"
        rm.kosher_code = "kosh"
        rm.save()
        
        q.put(lorem_one)
        q.put(lorem_two)
        q.put(lorem_three)
        print rm