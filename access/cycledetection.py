import networkx as nx

from access.models import Formula, Flavor, Ingredient, FormulaCycleException

class FormulaNode():
    counter=0
    
    def __init__(self, flavor):
        self.id = flavor.id
        self.counter = FormulaNode.counter
        FormulaNode.counter = FormulaNode.counter+1
        
        
    def get_flavor(self):
        return Flavor.objects.get(id=self.id)
        
    def __unicode__(self):
        f = Flavor.objects.get(id=self.id)
        return f.__unicode__()
    
    def __str__(self):
        f = Flavor.objects.get(id=self.id)
        #return str(f.__unicode__())
        return str("%s - %s" % (f.__unicode__(), self.counter))
        
class FormulaTree(): #unique nodes
    
    def __init__(self, flavor):
        self.g = nx.DiGraph()
        self.g.root = FormulaNode(flavor)
        self.expand_node(self.g.root)
        
    def get_leaves(self):
        return list(n for n,d in self.g.out_degree_iter() if d==0)
        
    def expand_node(self, node):
        
        starbunch = [node,]
        starbunch.extend(map(FormulaNode, node.get_flavor().get_gazintas()))
        self.g.add_star(starbunch)
        
    def expand_leaves(self):
        leaves = self.get_leaves()
        for leaf in leaves:
            self.expand_node(leaf)

class CycleDetection():
    """Record the flavor number of all cycles in the database.
    """
    debug=False
    
    def re_init(self):
        """Initializes values so that data from previous calls doesn't
        pollute later calls.
        """
        self.visited_flavors = {}
        self.cycled_flavors = {}
        self.other_exceptions = {}
    
    def check_all_flavors(self):
        """Iterates over all flavors, looking for cycles and other
        related exceptions.
        """
        self.re_init()
        for flavor in Flavor.objects.all().order_by('number'):
            if not flavor.number in self.visited_flavors:
                print "Checking: %s" % flavor
                self.inner_check_flavor(flavor, {})
            else:
                print "Skipping: %s" % flavor

        print "Cycled flavors-"   
        print self.cycled_flavors             
        #for cycle in self.cycled_flavors.values():
        #    self.parse_cycled_flavor(cycle)
        print "Other exceptions-"
        print self.other_exceptions
                
    def check_flavor(self, flavor, parent_flavors={}):
        """Traverses a single flavor and checks to see if any gazintas
        are in a dictionary containing their parents' numbers. If yes, 
        then a FormulaCycleException is raised.
        """
        self.re_init()
        print "Checking: %s" % flavor
        self.inner_check_flavor(flavor, parent_flavors)
        print self.cycled_flavors
        print self.other_exceptions
        
    def inner_check_flavor(self, flavor, parent_flavors):
        """Traverses a flavor and checks to see if any gazintas are in
        a dictionary containing their parents' numbers. If yes, then a
        FormulaCycleException is raised. Assumes that self.(visited_flavors,
        cycled_flavors, other_exceptions) are initialized and contain
        valid data.       
        """
        if self.debug:
            print "Visited: %s" % self.visited_flavors 
        try:
            for gazinta in self.get_fresh_gazintas(flavor):
                if self.debug:
                    print "%s in %s" % (gazinta.number, self.visited_flavors)
                    print gazinta.number in self.visited_flavors
                if gazinta.number in parent_flavors:
                    raise FormulaCycleException(gazinta)
                print "Checking gazinta: %s" % gazinta
                gazinta_parents = parent_flavors.copy()
                gazinta_parents[flavor.number] = gazinta.number
                self.inner_check_flavor(gazinta, gazinta_parents)
  
        except FormulaCycleException as e:
            self.cycled_flavors[e.value] = parent_flavors
            self.visited_flavors[e.value.id] = 1
        except Exception as e:
            self.other_exceptions[flavor.number] = e
        self.visited_flavors[flavor.id] = 1
        
    def get_gazintas(self, flavor):
        """Returns a list of gazintas in a flavor.
        """
        gazintas = []
        for ingredient in Formula.objects.filter(flavor=flavor):
#            try
            if ingredient.ingredient.is_gazinta:
                gazintas.append(ingredient.gazinta())
#            except Exception as e:
#                pass
#                self.other_exceptions[ingredient.ingredient.number] = e.args
        return gazintas
        
    def freshness_check(self, flavor):
        """Returns true if a flavor hasn't been visited yet. Also adds
        the flavor to the list of visited flavors.
        """
        if flavor.id in self.visited_flavors:
            print "Skipping: %s" % flavor
            return False
        else:
            return True
        
    def get_fresh_gazintas(self, flavor):
        """Returns a list of gazintas in a flavor filtered through the
        freshness check.
        """
        return filter(self.freshness_check, self.get_gazintas(flavor))
    
    def parse_cycled_flavor(self, cycle_dict):
        values = cycle_dict.values()
        keys = cycle_dict.keys()
        root = None
        for key in keys:
            if not key in values:
                root = key
                break
        path = [key,]
        try:
            while True:
                key = cycle_dict[key] 
                path.append(key)
        except KeyError as e:
            pass
        for fid in path:
            print "%s ->" % Flavor.objects.get(id=fid)
