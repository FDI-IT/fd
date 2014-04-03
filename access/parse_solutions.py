import re
import csv
from decimal import Decimal
from django.db.models import Q
from fd.access.models import Ingredient

class SolutionFixer():
    percent_re = re.compile(r'((\d+(\.\d*)?)|\.\d+)\%')
    noise_words = [
          'pg',
          'etoh',
          'triacetin',
          'soybean',
          'in',
          'water',
          'oil',
          'neobee',
          'pin',
          'powder',
          'acid',
                 ]
    
    solvents = {
                'pg':703,
                'etoh':321,
                'triacetin':829,
                'tria':829,
                'soybean oil':758,
                'soy bean oil':758,
                'soybeanoil':758,
                'neobee':1983,
                }
         
    noise_res = [
                    re.compile(r'#'),
                    re.compile(r''),
                    re.compile(r'\%'),
                    re.compile(r'pin\d+'),
                    ]

    solutions = Ingredient.objects.filter(suppliercode__iexact='fdi').filter(
                                         sub_flavor=None)
    rms = Ingredient.objects.filter(~Q(suppliercode__iexact='fdi'))
    
    def __init__(self):
       pass
    
    def get_name_fields(self, ingredient):
        return (ingredient.prefix.lower().replace('(', ' ').replace(')', ' '),
            ingredient.product_name.lower().replace('(', ' ').replace(')', ' '),           
            ingredient.part_name2.lower().replace('(', ' ').replace(')', ' '),
            ingredient.description.lower().replace('(', ' ').replace(')', ' '))
    
    def atomize_name(self, ingredient):
        """
        returns a list of search words, filtered against noise.
        """
        name_words = []
        name_fields = self.get_name_fields(ingredient)
        for field in name_fields:
            name_words = name_words + field.split()
            
        word_re = re.compile(r'^([a-zA-Z]+)(,|\.)$')
        for i in range(len(name_words)):
            try:
                name_words[i] = word_re.match(name_words[i]).group(1)
            except:
                pass
        
        return filter(self.name_filter, name_words)
        
    def compare_names(self, lhs, rhs):
        counter = 0
        left_atoms = self.atomize_name(lhs)
        right_atoms = self.atomize_name(rhs)
        for atom in left_atoms:
            if atom in right_atoms:
                counter += 1
        return counter

    def parse_percentage(self):
        self.headers.append('parsed_percentage')
        for row in self.solution_list:
            row.append(self.get_percentage(row))
            
    def get_solvent(self, ingredient):
        name = ingredient.product_name.lower()
        for solvent in SolutionFixer.solvents:
            if solvent in name:
                return SolutionFixer.solvents[solvent]
            
    def get_percentage(self, ingredient):
        name = ingredient.product_name
        percentage_match = SolutionFixer.percent_re.search(name)
        try:
            percentage = Decimal(percentage_match.group()[:-1])
        except:
            percentage = ''
        return percentage
        
    def name_filter(self, word):
        if word in SolutionFixer.noise_words:
            return False
            
        for noise_re in SolutionFixer.noise_res:
           my_match = noise_re.search(word)
        if my_match:
            return False
            
        return True
            
def test():        
    sf = SolutionFixer()
    first_solution = sf.solutions[0]
    first_solution_matches = {}
    for sol in sf.solutions[1:]:
        compare_count = sf.compare_names(first_solution, sol)
        if compare_count > 0:
            first_solution_matches[compare_count] = first_solution_matches.get(compare_count, []) + [sol]
            
    for k, v in first_solution_matches.iteritems():
        print "KEY: %s" % k
        for ing in v:
            pass
            #print ing
    