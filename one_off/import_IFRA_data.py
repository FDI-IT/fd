from access.models import Flavor, Ingredient

import pandas as pd
import numpy as np

from numpy import isnan

ifra_doc = pd.read_excel('ifra_aggregated_data.xlsx')

ifra_categories = [
    'ifra_cat1',
    'ifra_cat2',
    'ifra_cat3',
    'ifra_cat4',
    'ifra_cat5A',
    'ifra_cat5B',
    'ifra_cat5C',
    'ifra_cat5D',
    'ifra_cat6',
    'ifra_cat7A',
    'ifra_cat7B',
    'ifra_cat8',
    'ifra_cat9',
    'ifra_cat10A',
    'ifra_cat10B',
    'ifra_cat11A',
    'ifra_cat11B',
    'ifra_cat12'
]

def import_IFRA_data():
    for index, row in ifra_doc.iterrows():
        fdi_pin = row['PIN#']

        relevant_ingredients = Ingredient.objects.filter(id=fdi_pin)
        for ing in relevant_ingredients:
            print("Adding IFRA Values to Ingredient: %s" % ing)

            ing.ifra_standard_type = row['IFRA Standard type']

            for cat in ifra_categories:
                val = row[cat]
                if not isinstance(val, str) and not isnan(val):
                    setattr(ing, cat, val) #If the value is 'No Restriction' or empty, don't set any maximum value

            ing.save()