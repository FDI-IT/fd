import csv
import reversion

from django.contrib.auth.models import User
from access.models import Flavor

def fix_overwritten_flavors():
    with open('overwritten_flavor_fixes.csv', 'w+') as outfile:
        with open('overwritten_flavors.csv', 'rb') as infile:
            reader = csv.reader(infile, delimiter=',', quotechar='|')
            writer = csv.writer(outfile, delimiter=',', quotechar='|')

            writer.writerow(['Original Product Number', 'New Product Number', 'Experimentals Moved', 'Lots Moved', 'Notes'])

            for row in reader:
                #writer.writerow([row[3], row[5]])

                #original_number is the newly created flavor with the original number
                #need to move back any lots and experimentals that were associated with the original flavor and are currently attached to the new number

                original_number = None
                new_number = None
                try:
                    original_number = Flavor.objects.get(number=row[3])
                except Flavor.DoesNotExist:
                    writer.writerow([row[3], row[5], '', '', 'Original number %s does not exist.'])
                except ValueError:
                    pass

                #new_number is the old flavor that was overwritten with a new number
                try:
                    new_number = Flavor.objects.get(number=row[5])
                except Flavor.DoesNotExist:
                    writer.writerow([row[3], row[5], '', '','New number %s does not exist.'])
                except ValueError:
                    pass

                if original_number and new_number:
                    #move experimentals and lots from new_number to original_number
                    experimentals_moved = []
                    lots_moved = []

                    experimentals = ExperimentalLog.objects.filter(flavor=new_number)
                    lots = Lot.objects.filter(flavor=new_number)
                    ssis = SpecSheetInfo.objects.filter(flavor=new_number)

                    for exlog in experimentals:
                        experimentals_moved.append(exlog.__unicode__())
                        exlog.flavor = original_number
                        exlog.save()

                    for lot in lots:
                        lots_moved.append(lot.number)
                        lot.flavor = original_number
                        lot.save()

                    for ssi in ssis:
                        ssi.flavor = original_number
                        ssi.save()

                    writer.writerow([original_number.number, new_number.number, ', '.join(experimentals_moved), ', '.join(lots_moved)])

                    #add changes to reversion history
                    with reversion.create_revision():
                        comment = "Overwritten by flavor %s. " % new_number.number
                        if experimentals:
                            comment += "Reattached original experimental(s): %s. " % ', '.join(experimentals_moved)
                        if lots:
                            comment += "Reattached original lot(s): %s. " % ', '.join(lots_moved)
                        original_number.save()

                        reversion.set_comment(comment)
                        reversion.set_user(User.objects.get(username='matta'))

                    with reversion.create_revision():
                        new_number.save()
                        reversion.set_comment('Overwrote flavor %s. Moved experimentals and/or lots back to said original product #.' % original_number.number)
                        reversion.set_user(User.objects.get(username='matta'))








                    


