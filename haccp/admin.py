from haccp.models import CustomerComplaint, CorrectiveAction, CIPM, ReceivingLog, Supplier, KosherGroup, WaterTest, TobaccoBeetleTest, ThermometerTest
from django.contrib import admin
from reversion.admin import VersionAdmin

class CustomerComplaintAdmin(VersionAdmin):
    search_fields = ['customer__companyname','flavor_number','flavor_object__name','lot','description']
    exclude = ('flavor_object',)
admin.site.register(CustomerComplaint,CustomerComplaintAdmin)

class CorrectiveActionAdmin(VersionAdmin):
    search_field = ['description','comments','validation','action_plan','recommendation']
admin.site.register(CorrectiveAction, CorrectiveActionAdmin)

class CIPMAdmin(VersionAdmin):
    search_field = ['description','recommendations','action_plan','validation','comments']
admin.site.register(CIPM, CIPMAdmin)

admin.site.register(WaterTest)

