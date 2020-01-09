DATABASES = {
    'default': {
        'NAME': 'justink1', #mattdb #fd_migrate #matta (proxmox)
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'www-data',
        'PASSWORD': 'fdi',
        'HOST': '192.168.10.87',
    }
}

REACT_SERVER = 'http://192.168.10.90:3000'
SECRET_KEY = '=doe#s2k1d0hv+zl9ar*b44rc=(mpl@datvu1h=30h_kg1sclx'
