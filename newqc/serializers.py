from django.forms import widgets
from rest_framework import serializers
from newqc.models import Lot, Retain, TestCard
from access.models import Flavor

class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ('id', 'prefix', 'natart', 'number', 'name', 'label_type') 
 
class TestCardSerializer(serializers.ModelSerializer):
#     large = serializers.ImageField(source='large', blank=True)
#     thumbnail = serializers.ImageField(source='thumbnail', blank=True)
         
    class Meta:
        model = TestCard
        fields = ('id', 'image_hash', 'large', 'thumbnail', 'notes', 'scan_time', 'import_log', 'qc_time', 'retain', 'status',)
         
class RetainSerializer(serializers.ModelSerializer):
    testcards = TestCardSerializer(many=True)
     
    class Meta:
        model = Retain
        fields = ('id', 'retain', 'date', 'lot', 'status', 'notes', 'ir', 'testcards')
 
class LotSerializer(serializers.ModelSerializer):
    retains = RetainSerializer(many=True)
    flavor = FlavorSerializer(many=False)
     
    class Meta:
        model = Lot
        fields = ('id', 'number', 'date', 'sub_lot', 'status', 'amount', 'flavor', 'retains')
           
         
#     def validate_status(self):
#         if 

# class FlavorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Flavor
#         fields = ('id', 'prefix', 'natart', 'number', 'name', 'label_type') 
# 
# class TestCardSerializer(serializers.ModelSerializer):
# #     large = serializers.ImageField(source='large', blank=True)
# #     thumbnail = serializers.ImageField(source='thumbnail', blank=True)
#         
#     class Meta:
#         model = TestCard
#         fields = ('id', 'scan_time', 'qc_time', 'retain', 'status',)
#         
# class RetainSerializer(serializers.ModelSerializer):
#     testcards = TestCardSerializer(many=True)
#     
#     class Meta:
#         model = Retain
#         fields = ('id', 'retain', 'date', 'lot', 'testcards')
# 
# class LotSerializer(serializers.ModelSerializer):
#     retains = RetainSerializer(many=True)
#     flavor = FlavorSerializer(many=False)
#     
#     class Meta:
#         model = Lot
#         fields = ('id', 'number', 'date', 'sub_lot', 'status', 'amount', 'flavor', 'retains')
        
        
        