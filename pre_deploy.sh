#!/bin/bash
apt-get update
apt-get -fy upgrade 
apt-get -fy install mercurial 
mkdir -p /var/www/django/packages
mkdir -p /var/www/django/fd
cd /var/www/django/fd
(hg pull http://fdtrac:8080/fd && hg update) || hg clone http://fdtrac:8080/fd ./
/var/www/django/fd/deploy.sh
