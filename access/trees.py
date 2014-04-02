import networkx as nx

from fd.access.models import Formula, Flavor, Ingredient, FormulaCycleException

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
        
class GazintaTree():
    
    def __init__(self, flavor):
        self.g = nx.Graph()
        self.g.root = FormulaNode(flavor)
        self.expand_node(self.g.root)
        
    def get_leaves(self):
        return list(n for n,d in self.g.degree_iter() if d==1)
        
    def expand_node(self, node):
        
        starbunch = [node,]
        starbunch.extend(map(FormulaNode, node.get_flavor().get_gazintas()))
        self.g.add_star(starbunch)
        
    def expand_leaves(self):
        leaves = self.get_leaves()
        for leaf in leaves:
            self.expand_node(leaf)