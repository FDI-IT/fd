#!/bin/bash -i
echo "deb http://apt.postgresql.org/pub/repos/apt/ utopic-pgdg main" >> /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

apt-get update

apt-get -fy upgrade 

apt-get -y install build-essential tmux vim apache2 apache2-bin \
    apache2-data apache2-mpm-worker libapache2-mod-wsgi rsync python-pip \
    python-dev glabels glabels-dev glabels-data openssh-server memcached \
    libboost-python-dev libzbar-dev libcurl4-gnutls-dev \
    libpq-dev man postgresql-client-9.3 gettext zlib1g-dev libjpeg-dev \
    redis-server default-jre cifs-utils
    
pip install virtualenv virtualenvwrapper

echo "export WORKON_HOME=/var/www/.virtualenvs" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
chmod -R 777 /var/www
source ~/.bashrc

mkvirtualenv fd1.11
workon fd1.11

pip install -r /var/www/django/fd/requirements.txt

# Monkey patching this line in Django to get admin to work with our super long model names
sed -i.BAK "s/name = models.CharField(_('name'), max_length=50)/name = models.CharField(_('name'), max_length=255) # MONKEYPATCHED! MONKEY PATCHED!/" /var/www/.virtualenvs/fd1.11/local/lib/python2.7/site-packages/django/contrib/auth/models.py

# Monkey patching installed app 'formsetfield', Django 1.7: forms.util -> forms.utils 
sed -i '50s/util/utils/' /var/www/.virtualenvs/fd1.11/local/lib/python2.7/site-packages/formfieldset/forms.py

#Monkey patching reversion; Django 1.7: Opts.module_name -> Opts.model_name
sed -i '136s/module_name/model_name/' /var/www/.virtualenvs/fd1.11/local/lib/python2.7/site-packages/reversion/admin.py

cd /var/www/django/packages
python setup.py install

cd /var/www/django/fd
ln -s /var/www/django/fd/django_apache_wsgi.conf /etc/apache2/sites-enabled/
ln -s /etc/apache2/sites-enabled/django_apache_wsgi.conf /etc/apache2/sites-available/

mkdir /var/www/djangomedia

mkdir /var/www/static_root
ln -s /var/www/.virtualenvs/fd1.11/local/lib/python2.7/site-packages/django/contrib/admin/static/admin /var/www/static_root/admin
ln -s /var/www/django/fd/staticmedia/css /var/www/static_root/css
ln -s /var/www/django/fd/staticmedia/js /var/www/static_root/js
ln -s /var/www/django/fd/staticmedia/images /var/www/static_root/images

chown -R www-data:www-data /var/www
mkdir /var/log/django
touch /var/log/django/newqc.log
touch /var/log/django/ghs.log
touch /var/log/django/scan_docs.log
chmod -R 777 /var/log/django
mkdir /srv/samba
chown -R www-data:www-data /srv/samba

echo -e "[trusted]\ngroups = www-data\nusers = www-data" > /etc/mercurial/hgrc.d/trust.rc

chsh -s /bin/bash www-data

echo "ServerName localhost" > /etc/apache2/conf-available/servername.conf
a2enconf servername
service apache2 reload

service apache2 restart



