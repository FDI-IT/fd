from access.models import FlavorSpecification

def create_new_spec(flavor, name, specification, micro, customer = None, replaces = None):
    flavorspec = FlavorSpecification(
                    flavor = flavor,
                    customer = customer,
                    name = name,
                    specification = specification,
                    micro = micro,
                    replaces = replaces,
                )
    flavorspec.save() 
    
def update_spec(spec, name, specification, micro):
    spec.name = name
    spec.specification = specification
    spec.micro = micro
    spec.save()
    
def delete_specification(spec):
    spec.delete()