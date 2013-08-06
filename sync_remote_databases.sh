#!/bin/bash

pg_dump -c -U postgres -h $1 fd_test | psql -U postgres