from access.models import Flavor, ExperimentalLog

def copy_from_e_to_f():
    for e in ExperimentalLog.objects.exclude(mixing_instructions=""):
        print(e.mixing_instructions)