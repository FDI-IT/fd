import os
import xlrd
from xlutils.copy import copy

from access.models import Flavor

def main():
    xr = xlrd.open_workbook('/srv/samba/tank/X Retains.xls')
    read_sheet = xr.sheets()[0]
    write_wb = copy(xr)
    write_sheet = write_wb.get_sheet(0)
    for r in range(4, read_sheet.nrows):
        flavornum = int(read_sheet.cell(r,0).value)
        print flavornum
        try:
            f = Flavor.objects.get(number=flavornum)
        except Flavor.DoesNotExist:
            write_sheet.write(r,1,"DNE")
            continue
        try:
            retains = f.combed_sorted_retain_superset()
            write_sheet.write(r,2,retains[0].date)
        except:
            continue
    write_wb.save('/srv/samba/tank/new.xls')

if __name__ == "__main__":
    main()
