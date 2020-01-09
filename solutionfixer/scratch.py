from datetime import date
from access.models import Ingredient, Flavor
from solutionfixer.models import Solution, SolutionStatus, SolutionMatchCache
s = Solution.objects.all()[10]
i = s.my_base
i = Ingredient()
i.id = 30000
i.product_name = "FOO"
i.part_name2 = "FOO"
i.purchase_price_update = date.today()
i.date_ordered = date.today()
i.lead_time = 1
i.unitsonorder = 1
i.unitsinstock=1
i.discontinued=False
i.unitprice = 10
i.prefix = 'ab'
i.comments = ''
i.cas = 'f'
i.committed = 1
i.fema = ''
i.art_nati = ''
i.kosher = ''
i.reorderlevel = 1
i.lastkoshdt = date.today()
i.solution = 1
i.solvent = 'abv'
i.suppliercode = 'e'
i.supplierid = 10
i.gmo = 'b'
i.natural_document_on_file = True
i.allergen = 'c'

#i.save()

i.rawmaterialcode = s.my_base.rawmaterialcode
i.save()

