#!/bin/bash
apt-get update
apt-get -fy upgrade 
apt-get -fy install mercurial 
mkdir -p /var/www/django/packages
hg clone http://fdtrac:8080/fd /var/www/django/fd
/var/www/django/fd/deploy.sh
