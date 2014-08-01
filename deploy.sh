#!/bin/bash
apt-get update

apt-get -fy upgrade 

apt-get -y install build-essential tmux vim ipython apache2 apache2-bin \
    apache2-data apache2-mpm-worker libapache2-mod-wsgi rsync python-pip \
    python-dev glabels glabels-dev glabels-data openssh-server memcached \
    libboost-python-dev python-pythonmagick libzbar-dev libcurl4-gnutls-dev \
    libpq-dev man postgresql-client-9.3 gettext zlib1g-dev libjpeg-dev

#setting up virtualenv and virtualenvwrapper
pip install virtualenv
pip install virtualenvwrapper
echo 'WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
source ~/.bashrc
mkvirtualenv fd_env
workon fd_env


pip install psycopg2 xlrd pycurl celery elaphe python-memcached \
    python-dateutil django==1.4.13 django-reversion==1.6.6 django-celery \
    django-formfieldset django-autocomplete-light south pillow
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

mkdir /var/www/djangomedia

mkdir /var/ww/static_root
ln -s /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin /var/www/static_root/admin
ln -s /var/www/django/fd/staticmedia/css /var/www/static_root/css
ln -s /var/www/django/fd/staticmedia/js /var/www/static_root/js
ln -s /var/www/django/fd/staticmedia/images /var/www/static_root/images

chown -R www-data:www-data /var/www
mkdir /var/log/django
chown -R www-data:www-data /var/log/django
mkdir /srv/samba
chown -R www-data:www-data /srv/samba
service apache2 restart