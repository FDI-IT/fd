from datetime import date

from newqc.models import Lot, get_next_lot_number, LotSOLIStamp

from access.models import Flavor, Customer

from salesorders.models import LineItem, SalesOrderNumber

from batchsheet.exceptions import BatchLotAddException

class BatchAddLots():    
    
    @staticmethod
    def add_lots(forms):
        extra_weight_lots = {}
        for form in forms:
            try:
                lot_flavor = Flavor.objects.get(number=form.cleaned_data['flavor_number'])
            except KeyError:
                print("LKJASLDFJAF ERROR")
            
            extra_weight = form.cleaned_data['extra_weight']
            amount = form.cleaned_data['amount'] + extra_weight
            
            new_lot = Lot(#number = cd['lot_number'],
                          number = get_next_lot_number(),
                          flavor = lot_flavor,
                          amount = amount,
                          status = 'Created')
            new_lot.save()
            
            if extra_weight > 0:
                extra_weight_lots[new_lot] = extra_weight
                
            
            soli_pk_list = eval(form.cleaned_data['details'])
            for soli_pk in soli_pk_list:
                soli = LineItem.objects.get(pk=soli_pk)
                if soli.covered == True:
                    raise BatchLotAddException('SOLI %s is already covered' % soli_pk)
                soli.covered=True
                soli.save()
                lss = LotSOLIStamp(
                            lot=new_lot, 
                            salesordernumber=soli.salesordernumber.number,
                            quantity=soli.quantity)
                lss.save()
            
            if len(extra_weight_lots) > 0:
                t = date.today()
                fdi_customer,created = Customer.objects.get_or_create(companyname='Flavor Dynamics, Inc. (Internal)')
                if created:
                    fdi_customer.save()
                s = SalesOrderNumber(number=SalesOrderNumber.get_next_internal_number(),
                                     customer=fdi_customer)
                s.save()
                for k,v in extra_weight_lots.items():
                    li = LineItem(salesordernumber=s,
                                  flavor=k.flavor,
                                  quantity=v,
                                  unit_price=0,
                                  quantity_price=0,
                                  ship_date=t,
                                  due_date=t,
                                  covered=True)
                    li.save()
                    lss = LotSOLIStamp(lot=k,
                                       salesordernumber=s.number,
                                       quantity=v)
                    lss.save()