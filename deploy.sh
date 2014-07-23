#!/bin/bash
apt-get update

apt-get -fy upgrade 

apt-get -y install build-essential tmux vim ipython apache2 apache2-bin apache2-data apache2-mpm-worker libapache2-mod-wsgi rsync python-pip python-dev glabels glabels-dev glabels-data openssh-server memcached libboost-python-dev python-pythonmagick libzbar-dev libcurl4-gnutls-dev libpq-dev

pip install psycopg2 xlrd pycurl celery elaphe python-memcached python-dateutil django==1.4.13 django-reversion==1.6.6 django-celery django-formfieldset
pip install --allow-external pil --allow-unverified pil pil 
pip install --allow-external zbar --allow-unverified zbar zbar 


# Monkey patching this line in Django to get admin to work with our super long model names
sed -i.BAK "s/name = models.CharField(_('name'), max_length=50)/name = models.CharField(_('name'), max_length=255) # MONKEYPATCHED! MONKEY PATCHED!/" /usr/local/lib/python2.7/dist-packages/django/contrib/auth/models.py

cd /var/www/django/packages
hg clone http://fdtrac:8080/ghs
cd ghs
python setup.py install

cd /var/www/django/fd
cp django_apache_wsgi.conf /etc/apache2/sites-available/
ln -s /etc/apache2/sites-available/django_apache_wsgi.conf /etc/apache2/sites-enabled/django_apache_wsgi.conf
ln -s /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin /var/www/djangoadminmedia

mkdir /var/www/djangomedia
ln -s /var/www/django/fd/staticmedia/css /var/www/djangomedia/css
ln -s /var/www/django/fd/staticmedia/js /var/www/djangomedia/js
ln -s /var/www/django/fd/staticmedia/images /var/www/djangomedia/images

chown -R www-data:www-data /var/www
mkdir /var/log/django
chown -R www-data:www-data /var/log/django
mkdir /srv/samba
chown -R www-data:www-data /srv/samba
service apache2 restart