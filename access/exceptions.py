        
class FormulaException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
        
class FormulaCycleException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):        
        return ("Cycle detected on the following sequence of "
                "flavor numbers: " + str(self.value))
        
    def build_failed_superlist(self):
        failed_flavor_numbers = self.value[:]
        self.failed_superlist = {}
        for cycle_flavor_number in failed_flavor_numbers:
            cycle_flavor = Flavor.objects.get(number=cycle_flavor_number)
            try:
                cycle_ingredient = cycle_flavor.ingredient_set.all()[0]
            except:
                self.failed_superlist[cycle_flavor.flavor.number] = 1
                continue
            cycle_formula_rows = Formula.objects.filter(ingredient=cycle_ingredient)
            for cfr in cycle_formula_rows:
                if cfr.flavor.number in self.failed_superlist:
                    pass
                else:
                    self.failed_superlist[cfr.flavor.number] = 1
                    failed_flavor_numbers.append(cfr.flavor.number)
        return self.failed_superlist
    
class FormulaWeightException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return "Flavor ingredients do not add to 1000: %s" % repr(self.value)
