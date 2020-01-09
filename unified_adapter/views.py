# TODO:    change row amounts according to form value
#          change page appearance after print link is pressed

from unified_adapter.datagrids import ProductInfoDataGrid

def pa_list(request):
    return ProductInfoDataGrid(request).render(request, 'unified_adapter/pa_list.html')