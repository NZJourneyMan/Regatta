#!/bin/bash

pg_dump -d $HEROKU_DATABASE_URL > dswcregetta-$(date +%y-%m-%d).dbdump
