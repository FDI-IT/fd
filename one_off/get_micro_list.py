
import os
import sys
sys.path.append('/usr/local/django/fd')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ["CELERY_LOADER"] = "django"
from access.models import Ingredient
def main():
    print
    for i in Ingredient.objects.filter(microsensitive="MICROSENSITIVE"):
        print i.pk
    print
if __name__ == "__main__":
    main()
