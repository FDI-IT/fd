from django.contrib.auth.models import User
from rest_framework import serializers, metadata
from access.models import Flavor, flavor_api_fields, Ingredient, LeafWeight
from flavor_usage.models import Tag, ApplicationType

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('api_url','username','email')

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields).union(set(self.default_fields))
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class FlavorSerializer(DynamicFieldsModelSerializer):

    gmo = serializers.ReadOnlyField()

    tags = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    leaf_weights = serializers.SerializerMethodField()
    formula_weights = serializers.SerializerMethodField()

    # these fields will be serialized no matter what even if a 'fields' parameter is supplied
    default_fields = ['id', 'prefix', 'number', 'natart', 'name']

    class Meta:
        model = Flavor
        fields =  flavor_api_fields + ['tags','applications','leaf_weights','formula_weights', 'gmo']

        # flavor_searchable_fields = Flavor.api_searchable_fields
        # fields = flavor_searchable_fields.append('api_url')

    def get_tags(self, obj):
        return obj.tag_set.all().values_list('name',flat=True)

    def get_applications(self, obj):
        return obj.applications.all().values_list('application_type__name',flat=True)

    def get_leaf_weights(self, obj):
        return dict(obj.leaf_weights.all().values_list('ingredient__id','weight'))

    def get_formula_weights(self, obj):
        return dict(obj.formula_set.all().values_list('ingredient__id','amount'))

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id','art_nati','prefix','product_name']

class LeafWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeafWeight
        fields = ['root_flavor','ingredient','weight']

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('name','flavor')

#This provides the OPTIONS request API endpoint for flavors - primarily used for dropdown options in the search view
class FDIMetadata(metadata.BaseMetadata):
    def determine_metadata(self, request, view):
        options_dict = {}
        options_dict['flavor'] = {}

        #Get option fields - we don't need all possible options for name, number, id, etc.
        flavor_option_fields = [field for field in flavor_api_fields if field not in ['name','number','id', 'flashpoint', 'prefix']]

        for field in flavor_option_fields:
            options_dict['flavor'][field] = Flavor.objects.values_list(field,flat=True).distinct().order_by()

        options_dict['tag'] = {}
        options_dict['tag']['name'] = Tag.objects.values_list('name',flat=True).distinct().order_by()

        options_dict['applicationtype'] = {}
        options_dict['applicationtype']['name'] = ApplicationType.objects.values_list('name',flat=True).distinct().order_by()

        options_dict['flavor']['gmo'] = ['GMO Free', 'GMO Non-Detect', 'Genetically Modified']

        return options_dict
